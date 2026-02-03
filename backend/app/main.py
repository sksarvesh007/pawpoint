"""PawPoint Backend - Main Application Entry Point."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.redis import close_redis, init_redis
from app.core.telemetry import init_telemetry, shutdown_telemetry
from app.db import close_db, init_db

# Export API keys to environment for Pydantic AI and other libraries
# Pydantic Settings loads from .env files but doesn't export to os.environ
# We need to explicitly set them so Pydantic AI can access them
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key.get_secret_value()
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown events."""
    # Configure Loguru logging first
    configure_logging(
        debug=settings.debug,
        json_logs=settings.is_production,
        log_level="DEBUG" if settings.debug else "INFO",
    )

    # Startup
    logger.info("Starting application: {} v{}", settings.app_name, settings.app_version)
    logger.info("Environment: {}", settings.app_env.value)
    logger.info("Debug mode: {}", settings.debug)

    # Initialize OpenTelemetry
    init_telemetry(app, settings)
    logger.info("Telemetry and observability initialized")

    # Initialize database
    try:
        await init_db()
        logger.info("Database connection pool initialized")
    except ConnectionError as e:
        logger.error("Database initialization failed: {}", str(e))
        logger.error("Application cannot start without a database connection")
        raise

    # Initialize Redis
    try:
        await init_redis()
        logger.info("Redis connection established")
    except ConnectionError as e:
        logger.error("Redis initialization failed: {}", str(e))
        logger.error("Application cannot start without a Redis connection")
        raise

    yield

    # Shutdown
    await close_redis()
    await close_db()
    shutdown_telemetry(app)
    logger.info("Application shutdown complete: {}", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="AI-powered veterinary engagement platform",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
)

# Register rate limiter with the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# CORS configuration from settings
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - health check."""
    return {"status": "healthy", "service": "pawpoint-api"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for deployment platforms."""
    return {
        "status": "ok",
        "environment": settings.app_env.value,
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint() -> PlainTextResponse:
    """Prometheus metrics endpoint for scraping."""
    return PlainTextResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/config")
async def config_info() -> dict[str, str | bool | list[str]]:
    """Configuration info endpoint (disabled in production)."""
    if settings.is_production:
        return {"error": "Not available in production"}

    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.app_env.value,
        "debug": settings.debug,
        "allowed_origins": settings.allowed_origins,
        "telemetry_enabled": settings.otel_enabled,
    }
