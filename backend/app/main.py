"""PawPoint Backend - Main Application Entry Point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.telemetry import init_telemetry, shutdown_telemetry
from app.db import close_db, init_db


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
    logger.info("🐾 Starting {} v{}", settings.app_name, settings.app_version)
    logger.info("📍 Environment: {}", settings.app_env.value)
    logger.info("🔧 Debug mode: {}", settings.debug)

    # Initialize OpenTelemetry
    init_telemetry(app, settings)
    logger.info("📊 Telemetry initialized")

    # Initialize database
    await init_db()
    logger.info("🗄️ Database initialized")

    yield

    # Shutdown
    await close_db()
    shutdown_telemetry(app)
    logger.info("👋 Shutting down {}", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="AI-powered veterinary engagement platform",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
)

# CORS configuration from settings
app.add_middleware(
    CORSMiddleware,
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
