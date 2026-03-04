"""
Embedded LiveKit Agent Runner

Runs the LiveKit agent worker as a background task within the FastAPI process.
This allows running the agent without a separate background worker service.

Usage (from FastAPI lifespan):
    from livekit_agent.embedded import start_embedded_agent, stop_embedded_agent

    async def lifespan(app):
        agent_task = await start_embedded_agent()
        yield
        await stop_embedded_agent(agent_task)
"""

import asyncio
import contextlib
import logging
import os
from typing import Any

# Import settings first to get config
from app.core.config import settings

logger = logging.getLogger(__name__)

# Set embedded flag BEFORE importing agent modules
# This tells agent config to read from environment instead of dev.env
os.environ["LIVEKIT_AGENT_EMBEDDED"] = "true"

# Export all required environment variables for the agent
# These must be set before the agent config module is imported
if settings.database_url:
    os.environ["DATABASE_URL"] = settings.database_url
if settings.redis_url:
    os.environ["REDIS_URL"] = settings.redis_url
if settings.livekit_api_key:
    os.environ["LIVEKIT_API_KEY"] = settings.livekit_api_key
if settings.livekit_api_secret:
    os.environ["LIVEKIT_API_SECRET"] = settings.livekit_api_secret.get_secret_value()
if settings.livekit_url:
    os.environ["LIVEKIT_URL"] = settings.livekit_url
if settings.deepseek_api_key:
    os.environ["DEEPSEEK_API_KEY"] = settings.deepseek_api_key.get_secret_value()
if settings.deepseek_base_url:
    os.environ["DEEPSEEK_BASE_URL"] = settings.deepseek_base_url
if settings.assemblyai_api_key:
    os.environ["ASSEMBLYAI_API_KEY"] = settings.assemblyai_api_key.get_secret_value()
if settings.cartesia_api_key:
    os.environ["CARTESIA_API_KEY"] = settings.cartesia_api_key.get_secret_value()

# Global reference to the worker for cleanup
_worker: Any = None  # Type: Worker | None (imported at runtime)
_agent_task: asyncio.Task[Any] | None = None


def _setup_environment() -> None:
    """Set up environment variables for LiveKit plugins."""
    # Some plugins read API keys from environment variables
    if settings.assemblyai_api_key:
        os.environ["ASSEMBLYAI_API_KEY"] = (
            settings.assemblyai_api_key.get_secret_value()
        )
    if settings.cartesia_api_key:
        os.environ["CARTESIA_API_KEY"] = settings.cartesia_api_key.get_secret_value()
    if settings.deepseek_api_key:
        # OpenAI plugin reads OPENAI_API_KEY
        os.environ["OPENAI_API_KEY"] = settings.deepseek_api_key.get_secret_value()


async def start_embedded_agent() -> asyncio.Task[Any] | None:
    """
    Start the LiveKit agent as a background task.

    Returns:
        The asyncio task running the agent, or None if agent is disabled/misconfigured.
    """
    global _worker, _agent_task

    # Check if embedded agent is enabled
    if not settings.livekit_agent_embedded:
        logger.info("Embedded LiveKit agent is disabled")
        return None

    # Check required configuration
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        logger.warning("LiveKit API credentials not configured - agent will not start")
        return None

    if not settings.livekit_url:
        logger.warning("LiveKit URL not configured - agent will not start")
        return None

    # Set up environment for plugins
    _setup_environment()

    # Import here to avoid issues when livekit-agents isn't installed
    from livekit.agents import Worker, WorkerOptions

    # Import entrypoint here to avoid circular imports
    from livekit_agent.main import entrypoint

    logger.info("Starting embedded LiveKit agent...")
    logger.info(f"  - LiveKit URL: {settings.livekit_url}")
    logger.info(f"  - API Key: {settings.livekit_api_key[:8]}...")

    # Create worker with app settings
    _worker = Worker(
        opts=WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret.get_secret_value(),
            ws_url=settings.livekit_url,
        ),
    )

    async def run_worker() -> None:
        """Run the worker and handle exceptions."""
        try:
            await _worker.run()
        except asyncio.CancelledError:
            logger.info("Embedded agent task cancelled")
        except Exception as e:
            logger.error(f"Embedded agent error: {e}")
            raise

    # Start worker as background task
    _agent_task = asyncio.create_task(run_worker(), name="livekit-agent-worker")
    logger.info("Embedded LiveKit agent started successfully")

    return _agent_task


async def stop_embedded_agent(task: asyncio.Task[Any] | None = None) -> None:
    """
    Stop the embedded LiveKit agent gracefully.

    Args:
        task: The agent task to stop (optional, uses global reference if not provided)
    """
    global _worker, _agent_task

    task_to_stop = task or _agent_task

    if task_to_stop is None:
        logger.debug("No embedded agent task to stop")
        return

    logger.info("Stopping embedded LiveKit agent...")

    # Close the worker gracefully
    if _worker is not None:
        try:
            await asyncio.wait_for(
                _worker.aclose(),
                timeout=settings.livekit_agent_shutdown_timeout,
            )
        except TimeoutError:
            logger.warning("Agent shutdown timed out, forcing cancellation")
        except Exception as e:
            logger.error(f"Error during agent shutdown: {e}")

    # Cancel the task if still running
    if not task_to_stop.done():
        task_to_stop.cancel()
        with contextlib.suppress(TimeoutError, asyncio.CancelledError):
            await asyncio.wait_for(task_to_stop, timeout=5.0)

    _worker = None
    _agent_task = None
    logger.info("Embedded LiveKit agent stopped")
