"""Redis client dependency for FastAPI.

Provides async Redis connection for caching and session management.
"""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings

# Global Redis client (initialized on startup)
_redis_client: Redis | None = None


async def init_redis() -> None:
    """Initialize Redis connection pool.

    Call this on application startup.
    """
    from loguru import logger

    global _redis_client

    if settings.redis_url:
        logger.info(f"Connecting to Redis at {settings.redis_url}")
        _redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=settings.redis_socket_connect_timeout,
            socket_timeout=settings.redis_socket_timeout,
        )
        # Test connection
        try:
            await _redis_client.ping()
            logger.info("Redis connection successful")
        except ConnectionRefusedError as e:
            logger.error(f"Redis connection failed: {e}")
            raise ConnectionError(
                f"Failed to connect to Redis at {settings.redis_url}. "
                "Is Redis running? Try: docker compose up db (includes Redis)"
            ) from e
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise ConnectionError(
                f"Redis initialization failed: {e.__class__.__name__}: {e}"
            ) from e


async def close_redis() -> None:
    """Close Redis connection.

    Call this on application shutdown.
    """
    global _redis_client

    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


async def get_redis() -> AsyncGenerator[Redis]:
    """Get Redis client for dependency injection.

    Usage:
        @router.get("/")
        async def endpoint(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value")

    Yields:
        Redis client instance

    Raises:
        RuntimeError: If Redis is not initialized
    """
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call init_redis() on application startup."
        )

    yield _redis_client


def get_redis_client() -> Redis | None:
    """Get Redis client directly (non-dependency).

    Returns:
        Redis client or None if not initialized
    """
    return _redis_client
