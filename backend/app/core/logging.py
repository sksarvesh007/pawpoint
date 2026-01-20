"""Logging configuration using Loguru with OpenTelemetry trace correlation.

Provides:
- Structured JSON logging for production
- Pretty colored console logging for development
- Automatic trace/span ID injection from OpenTelemetry
- File rotation and retention
"""

import logging
import sys
from typing import TYPE_CHECKING

from loguru import logger
from opentelemetry import trace

if TYPE_CHECKING:
    from loguru import Record


def get_trace_context() -> dict[str, str]:
    """Extract current OpenTelemetry trace context."""
    span = trace.get_current_span()
    ctx = span.get_span_context()

    if ctx.is_valid:
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
        }
    return {"trace_id": "0", "span_id": "0"}


def trace_injection(record: "Record") -> None:
    """Inject trace context into log record."""
    trace_ctx = get_trace_context()
    record["extra"]["trace_id"] = trace_ctx["trace_id"]
    record["extra"]["span_id"] = trace_ctx["span_id"]


class InterceptHandler(logging.Handler):
    """Handler to intercept standard logging and send to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the log originated
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging(
    debug: bool = True,
    json_logs: bool = False,
    log_level: str = "DEBUG",
) -> None:
    """Configure Loguru logger with appropriate handlers.

    Args:
        debug: If True, use pretty console logging; if False, use JSON
        json_logs: Force JSON logging regardless of debug mode
        log_level: Minimum log level to capture
    """
    # Remove default handler
    logger.remove()

    # Add trace context injection
    logger.configure(patcher=trace_injection)

    if debug and not json_logs:
        # Development: Pretty console output with colors
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[trace_id]:.8}:{extra[span_id]:.8}</cyan> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # Production: Structured JSON logging
        logger.add(
            sys.stderr,
            format="{message}",
            level=log_level,
            serialize=True,  # JSON output
            backtrace=True,
            diagnose=False,  # Don't expose variable values in prod
        )

    # File logging with rotation (always enabled)
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[trace_id]}:{extra[span_id]} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="10 days",
        compression="zip",
        backtrace=True,
        diagnose=False,
    )

    # Error-specific log file
    logger.add(
        "logs/errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[trace_id]}:{extra[span_id]} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,  # Include variable values for error debugging
    )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept uvicorn and other library loggers
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    logger.info(
        "Loguru logging configured", debug=debug, json_logs=json_logs, level=log_level
    )


# Export configured logger
__all__ = ["InterceptHandler", "configure_logging", "logger"]
