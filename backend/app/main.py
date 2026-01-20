"""PawPoint Backend - Main Application Entry Point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    print(f"🐾 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Environment: {settings.app_env.value}")
    print(f"🔧 Debug mode: {settings.debug}")
    yield
    # Shutdown
    print(f"👋 Shutting down {settings.app_name}")


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
    }
