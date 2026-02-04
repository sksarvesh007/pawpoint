"""Custom metrics and tracing instrumentation for PawPoint.

Provides:
- Application-specific metrics following OTel semantic conventions
- Path normalization for cardinality control
- Decorator for automatic function tracing
"""

import functools
import re
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from app.core.telemetry import get_meter, get_tracer

if TYPE_CHECKING:
    from opentelemetry.metrics import Histogram

# Type variables for generic decorator
P = ParamSpec("P")
R = TypeVar("R")

# Get meter and tracer instances
meter = get_meter("pawpoint")
tracer = get_tracer("pawpoint")

# =============================================================================
# Counters (use _total suffix per OTel conventions)
# =============================================================================

api_requests_total = meter.create_counter(
    name="pawpoint_api_requests_total",
    description="Total API requests",
    unit="1",
)

chat_messages_total = meter.create_counter(
    name="pawpoint_chat_messages_total",
    description="Total chat messages processed",
    unit="1",
)

chat_tokens_total = meter.create_counter(
    name="pawpoint_chat_tokens_total",
    description="Total tokens used in chat",
    unit="1",
)

db_queries_total = meter.create_counter(
    name="pawpoint_db_queries_total",
    description="Total database queries executed",
    unit="1",
)

auth_attempts_total = meter.create_counter(
    name="pawpoint_auth_attempts_total",
    description="Total authentication attempts",
    unit="1",
)

# =============================================================================
# Histograms (use _seconds suffix for duration per OTel conventions)
# =============================================================================

api_request_duration_seconds = meter.create_histogram(
    name="pawpoint_api_request_duration_seconds",
    description="API request duration",
    unit="s",
)

chat_response_duration_seconds = meter.create_histogram(
    name="pawpoint_chat_response_duration_seconds",
    description="Chat response latency",
    unit="s",
)

db_query_duration_seconds = meter.create_histogram(
    name="pawpoint_db_query_duration_seconds",
    description="Database query duration",
    unit="s",
)

llm_request_duration_seconds = meter.create_histogram(
    name="pawpoint_llm_request_duration_seconds",
    description="LLM API request duration",
    unit="s",
)

# =============================================================================
# Gauges (current state metrics)
# =============================================================================

active_websocket_connections = meter.create_up_down_counter(
    name="pawpoint_active_websocket_connections",
    description="Current active WebSocket connections",
    unit="1",
)

active_chat_sessions = meter.create_up_down_counter(
    name="pawpoint_active_chat_sessions",
    description="Current active chat sessions",
    unit="1",
)


# =============================================================================
# Path Normalization (prevents metric cardinality explosion)
# =============================================================================


def normalize_path(path: str) -> str:
    """Normalize paths to prevent metric cardinality explosion.

    Replaces UUIDs and numeric IDs with placeholders.

    Examples:
        /api/v1/patients/550e8400-e29b-41d4-a716-446655440000 -> /api/v1/patients/{id}
        /api/v1/clinics/123/settings -> /api/v1/clinics/{id}/settings
        /api/v1/appointments/2024-01-15 -> /api/v1/appointments/{date}
    """
    # Replace UUIDs (standard format)
    path = re.sub(
        r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "/{id}",
        path,
        flags=re.IGNORECASE,
    )

    # Replace numeric IDs (digits only)
    path = re.sub(r"/\d+", "/{id}", path)

    # Replace date patterns (YYYY-MM-DD)
    path = re.sub(r"/\d{4}-\d{2}-\d{2}", "/{date}", path)

    return path


# =============================================================================
# Tracing Decorator
# =============================================================================


def traced(
    span_name: str | None = None,
    attributes: dict[str, str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to add tracing to functions.

    Supports both sync and async functions. Automatically records exceptions.

    Args:
        span_name: Custom span name. Defaults to module.function_name
        attributes: Additional span attributes to set

    Usage:
        @traced()
        def my_function():
            ...

        @traced(span_name="custom-operation")
        async def my_async_function():
            ...

        @traced(attributes={"operation.type": "database"})
        def db_operation():
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = span_name or f"{getattr(func, '__module__', __name__)}.{getattr(func, '__qualname__', 'unknown')}"

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    # Cast is safe: we check func is async before calling async_wrapper
                    result = await func(*args, **kwargs)  # type: ignore[misc]
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(
                        create_error_status(e),
                    )
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(
                        create_error_status(e),
                    )
                    raise

        # Import here to check if coroutine
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper

    return decorator


def create_error_status(exception: Exception):
    """Create a trace status from an exception."""
    from opentelemetry.trace import Status, StatusCode

    return Status(StatusCode.ERROR, str(exception))


# =============================================================================
# Timing Context Manager
# =============================================================================


class Timer:
    """Context manager for timing operations and recording to histograms.

    Usage:
        with Timer(api_request_duration_seconds, {"method": "GET", "path": "/api/health"}):
            # do work
            ...
    """

    def __init__(
        self,
        histogram: "Histogram",
        attributes: dict[str, str] | None = None,
    ) -> None:
        self.histogram = histogram
        self.attributes = attributes or {}
        self.start_time: float = 0

    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        duration = time.perf_counter() - self.start_time
        self.histogram.record(duration, self.attributes)


# =============================================================================
# Helper Functions
# =============================================================================


def record_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
) -> None:
    """Record an API request with normalized path.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path (will be normalized)
        status_code: HTTP response status code
        duration_seconds: Request duration in seconds
    """
    normalized = normalize_path(path)
    attributes = {
        "method": method,
        "path": normalized,
        "status_code": str(status_code),
    }
    api_requests_total.add(1, attributes)
    api_request_duration_seconds.record(duration_seconds, attributes)


def record_chat_message(
    clinic_id: str,
    session_id: str,
    role: str,
    tokens: int = 0,
) -> None:
    """Record a chat message metric.

    Args:
        clinic_id: Clinic identifier
        session_id: Chat session identifier
        role: Message role (user, assistant, system)
        tokens: Number of tokens used
    """
    attributes = {
        "clinic_id": clinic_id,
        "role": role,
    }
    chat_messages_total.add(1, attributes)
    if tokens > 0:
        chat_tokens_total.add(tokens, attributes)


def record_llm_request(
    model: str,
    operation: str,
    duration_seconds: float,
    success: bool = True,
) -> None:
    """Record an LLM API request.

    Args:
        model: LLM model name
        operation: Type of operation (chat, completion, embedding)
        duration_seconds: Request duration in seconds
        success: Whether the request succeeded
    """
    attributes = {
        "model": model,
        "operation": operation,
        "success": str(success).lower(),
    }
    llm_request_duration_seconds.record(duration_seconds, attributes)


def record_db_query(
    operation: str,
    table: str,
    duration_seconds: float,
) -> None:
    """Record a database query metric.

    Args:
        operation: Query operation (select, insert, update, delete)
        table: Table name
        duration_seconds: Query duration in seconds
    """
    attributes = {
        "operation": operation,
        "table": table,
    }
    db_queries_total.add(1, attributes)
    db_query_duration_seconds.record(duration_seconds, attributes)
