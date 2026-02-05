"""
LiveKit Agent Configuration

Settings specific to the LiveKit agent worker.

When running standalone: reads from dev.env (or ENV_FILE)
When running embedded in FastAPI: inherits environment from parent process
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend directory (parent of livekit_agent)
_BACKEND_DIR = Path(__file__).resolve().parent.parent

# Determine env file - skip if running embedded (env vars already set by FastAPI)
# Check if we're running embedded by looking for LIVEKIT_AGENT_EMBEDDED env var
_IS_EMBEDDED = os.getenv("LIVEKIT_AGENT_EMBEDDED", "false").lower() == "true"
_ENV_FILE = (
    None if _IS_EMBEDDED else os.getenv("ENV_FILE", str(_BACKEND_DIR / "dev.env"))
)


class AgentSettings(BaseSettings):
    """LiveKit agent-specific settings."""

    # When embedded, env_file is None so we only read from environment variables
    # When standalone, we read from the specified env file
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LiveKit Configuration
    livekit_api_key: str
    livekit_api_secret: SecretStr
    livekit_url: str = "ws://livekit:7880"

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # DeepSeek LLM (primary AI provider)
    deepseek_api_key: SecretStr
    deepseek_base_url: str = "https://api.lkeap.cloud.tencent.com/v1"
    deepseek_model: str = "deepseek-v3-0324"

    # Voice AI Providers
    assemblyai_api_key: SecretStr  # STT
    cartesia_api_key: SecretStr  # TTS
    cartesia_voice_id: str = (
        "79a125e8-cd45-4c13-8a67-188112f4dd22"  # Default Cartesia voice
    )

    # Agent Configuration
    max_concurrent_jobs: int = 10
    shutdown_timeout: float = 30.0

    # Database Pool Settings (dedicated pool for agent workers)
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_pre_ping: bool = True
    db_pool_recycle: int = 300  # Recycle connections every 5 minutes


@lru_cache
def get_agent_settings() -> AgentSettings:
    """Get cached agent settings instance."""
    return AgentSettings()  # type: ignore[call-arg]


agent_settings = get_agent_settings()
