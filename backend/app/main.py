"""PawPoint Backend - Main Application Entry Point."""

import os
import secrets
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from opentelemetry import metrics, trace
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1 import api_router
from app.core.config import settings
from app.core.instrumentation import (
    api_request_duration_seconds,
    api_requests_total,
    normalize_path,
)
from app.core.logging import configure_logging
from app.core.redis import close_redis, init_redis
from app.core.telemetry import init_telemetry, shutdown_telemetry
from app.db import close_db, init_db

# Security for metrics endpoint (auto_error=False allows optional auth in dev)
security = HTTPBasic(auto_error=False)

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


# Metrics middleware to capture HTTP request metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to capture HTTP request metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip metrics for health and metrics endpoints
        if request.url.path in ("/health", "/metrics", "/"):
            return await call_next(request)

        start_time = time.perf_counter()
        status_code = "500"  # Default for unhandled exceptions
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            return response
        except Exception:
            # Re-raise but ensure metrics are recorded
            raise
        finally:
            # Always record metrics, even on exceptions
            duration = time.perf_counter() - start_time
            path = normalize_path(request.url.path)
            method = request.method
            attributes = {"method": method, "path": path, "status_code": status_code}
            api_requests_total.add(1, attributes)
            api_request_duration_seconds.record(duration, attributes)


# Register rate limiter with the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Add metrics middleware
app.add_middleware(MetricsMiddleware)  # type: ignore[arg-type]

# CORS configuration from settings
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Allow browser to access response headers (needed for SSE)
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


def verify_metrics_auth(
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> bool:
    """Verify metrics endpoint credentials with constant-time comparison.

    In development without metrics_password configured, authentication is skipped.
    In production, valid credentials are required.
    """
    # Skip auth in development if not configured
    if settings.is_development and not settings.metrics_password:
        return True

    # Require auth configuration in production
    if not settings.metrics_password:
        raise HTTPException(
            status_code=500,
            detail="Metrics authentication not configured",
        )

    # No credentials provided but auth is required
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Constant-time comparison to prevent timing attacks
    correct_user = secrets.compare_digest(
        credentials.username.encode("utf8"),
        settings.metrics_username.encode("utf8"),
    )
    correct_pass = secrets.compare_digest(
        credentials.password.encode("utf8"),
        settings.metrics_password.get_secret_value().encode("utf8"),
    )

    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint(
    _auth: bool = Depends(verify_metrics_auth),
) -> PlainTextResponse:
    """Prometheus metrics endpoint for scraping.

    Protected by HTTP Basic authentication in production.
    """
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


@app.get("/health/telemetry")
async def telemetry_health() -> dict[str, bool | float | str]:
    """Health check for observability pipeline.

    Returns status of tracing and metrics providers,
    along with the current sampling rate.
    """
    tracer_provider = trace.get_tracer_provider()
    meter_provider = metrics.get_meter_provider()

    # Check for actual configured providers, not just no-op defaults
    # The SDK TracerProvider and MeterProvider indicate proper configuration
    tracer_type = type(tracer_provider).__name__
    meter_type = type(meter_provider).__name__

    # NoOpTracerProvider/ProxyTracerProvider indicate unconfigured state
    tracer_ok = tracer_type not in ("NoOpTracerProvider", "ProxyTracerProvider")
    meter_ok = meter_type not in ("NoOpMeterProvider", "ProxyMeterProvider")

    # Determine sampling rate (10% in production, 100% in dev)
    sampling_rate = 0.1 if settings.is_production else 1.0

    return {
        "tracer": tracer_ok,
        "tracer_provider": tracer_type,
        "meter": meter_ok,
        "meter_provider": meter_type,
        "sampling_rate": sampling_rate,
        "otel_enabled": settings.otel_enabled,
    }
