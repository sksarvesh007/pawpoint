"""Application configuration using Pydantic Settings.

Supports automatic loading from environment-specific .env files:
- Development: loads from dev.env
- Production: loads from prod.env

The environment is determined by the APP_ENV environment variable.
"""

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment modes."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


def get_env_file() -> str:
    """Determine which .env file to load based on APP_ENV."""
    app_env = os.getenv("APP_ENV", "development").lower()
    base_path = Path(__file__).resolve().parent.parent.parent  # backend/

    if app_env == "production":
        env_file = base_path / "prod.env"
    elif app_env == "testing":
        env_file = base_path / "test.env"
    else:
        env_file = base_path / "dev.env"

    # Fall back to .env if specific file doesn't exist
    if not env_file.exists():
        fallback = base_path / ".env"
        if fallback.exists():
            return str(fallback)

    return str(env_file)


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Automatically loads from dev.env or prod.env based on APP_ENV.

    Usage:
        from app.core.config import settings
        print(settings.app_name)
    """

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars not defined here
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_name: str = "PawPoint API"
    app_version: str = "0.1.0"
    app_env: Environment = Environment.DEVELOPMENT
    debug: bool = True
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        description="Secret key for JWT signing and encryption",
    )

    # -------------------------------------------------------------------------
    # Server
    # -------------------------------------------------------------------------
    host: str = "0.0.0.0"  # noqa: S104 - Intentional for Docker/container deployments
    port: int = 8000

    # -------------------------------------------------------------------------
    # CORS - stored as comma-separated string, parsed via computed_field
    # -------------------------------------------------------------------------
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="allowed_origins",
    )

    @computed_field
    @property
    def allowed_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [
            origin.strip()
            for origin in self.allowed_origins_str.split(",")
            if origin.strip()
        ]

    # -------------------------------------------------------------------------
    # Database (Optional - uncomment when needed)
    # -------------------------------------------------------------------------
    database_url: str | None = None
    database_echo: bool = False  # SQLAlchemy echo SQL statements

    # -------------------------------------------------------------------------
    # Redis (Optional - uncomment when needed)
    # -------------------------------------------------------------------------
    redis_url: str | None = None

    # -------------------------------------------------------------------------
    # JWT Authentication
    # -------------------------------------------------------------------------
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # -------------------------------------------------------------------------
    # External APIs (Optional)
    # -------------------------------------------------------------------------
    openai_api_key: SecretStr | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: SecretStr | None = None

    # -------------------------------------------------------------------------
    # PIMS Integration (Optional)
    # -------------------------------------------------------------------------
    ezyvet_client_id: str | None = None
    ezyvet_client_secret: SecretStr | None = None
    vetspire_api_key: SecretStr | None = None

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.app_env == Environment.TESTING


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.

    Returns:
        Settings instance with all configuration loaded.
    """
    return Settings()


# Global settings instance for convenience
settings = get_settings()
