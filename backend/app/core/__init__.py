"""Core configuration and utilities for PawPoint Backend."""

from app.core.config import get_settings, settings
from app.core.logging import configure_logging, logger
from app.core.telemetry import get_meter, get_tracer

__all__ = [
    "configure_logging",
    "get_meter",
    "get_settings",
    "get_tracer",
    "logger",
    "settings",
]
