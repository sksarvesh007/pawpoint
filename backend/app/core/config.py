"""Application configuration using Pydantic Settings.

Supports automatic loading from environment-specific .env files:
- Development: loads from dev.env
- Production: loads from prod.env

The environment is determined by the ENVIRONMENT constant below.
Change this constant to switch between dev and prod environments.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# =============================================================================
# ENVIRONMENT SELECTOR - Change this to switch between dev/prod
# =============================================================================
# Set to "development" for local development (uses dev.env)
# Set to "production" for production deployment (uses prod.env)
# Set to "testing" for running tests (uses test.env)
# =============================================================================
ENVIRONMENT: str = "development"  # 👈 CHANGE THIS TO "production" FOR PROD
# =============================================================================


class Environment(str, Enum):
    """Application environment modes."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


def get_env_file() -> str:
    """Determine which .env file to load based on ENVIRONMENT constant."""
    # Use the hardcoded ENVIRONMENT constant instead of os.getenv
    app_env = ENVIRONMENT.lower()
    base_path = Path(__file__).resolve().parent.parent.parent  # backend/

    if app_env == "production":
        env_file = base_path / "prod.env"
    elif app_env == "testing":
        env_file = base_path / "test.env"
    else:
        env_file = base_path / "dev.env"

    # Verify file exists
    if not env_file.exists():
        raise FileNotFoundError(
            f"Environment file not found: {env_file}\n"
            f"Expected file for environment '{app_env}'"
        )

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
        default=SecretStr("dev-insecure-key-for-local-development-only"),
        description="Secret key for JWT signing and encryption (min 32 chars in prod)",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: SecretStr, info) -> SecretStr:
        """Ensure secret key is strong enough for production."""
        key = v.get_secret_value()

        # Get app_env from values if available
        app_env = info.data.get("app_env", Environment.DEVELOPMENT)

        # Only enforce strict validation in production
        if app_env == Environment.PRODUCTION:
            # Reject obvious weak keys
            weak_keys = {
                "change-me",
                "changeme",
                "replace",
                "secret",
                "password",
                "test",
                "demo",
                "example",
            }

            if any(weak in key.lower() for weak in weak_keys):
                raise ValueError(
                    "Production secret key contains weak/placeholder text. "
                    "Generate a strong key with:\n"
                    "  python -c 'import secrets; print(secrets.token_urlsafe(64))'"
                )

            # Check length
            if len(key) < 32:
                raise ValueError(
                    f"Production secret key must be at least 32 characters. "
                    f"Current length: {len(key)}"
                )

            # Check for dev-specific keys in production
            if "dev" in key.lower() or "local" in key.lower():
                raise ValueError(
                    "Production secret key cannot contain 'dev' or 'local'. "
                    "Use a production-grade secret."
                )

        return v

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
    # Database
    # -------------------------------------------------------------------------
    database_url: str | None = Field(
        default=None,
        description="PostgreSQL database connection URL (required for operation)",
    )
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
    # OpenTelemetry / Observability
    # -------------------------------------------------------------------------
    otel_enabled: bool = True
    otel_service_name: str = "pawpoint-api"
    otel_exporter_otlp_endpoint: str | None = None  # e.g., http://alloy:4317
    otel_exporter_otlp_headers: str | None = None  # e.g., "Authorization=Basic xxx"
    prometheus_enabled: bool = True

    # -------------------------------------------------------------------------
    # Monitoring & Security
    # -------------------------------------------------------------------------
    metrics_username: str = Field(
        default="prometheus", description="Username for /metrics endpoint"
    )
    metrics_password: SecretStr | None = None  # Required in production
    sentry_dsn: SecretStr | None = None  # Optional error tracking

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
