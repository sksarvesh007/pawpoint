"""Custom metrics and tracing instrumentation for PawPoint.

Provides:
- Application-specific metrics following OTel semantic conventions
- Path normalization for cardinality control
- Decorator for automatic function tracing

IMPORTANT: Metrics and tracers are lazily initialized to ensure they use
the configured providers from init_telemetry() rather than no-op defaults.
"""

import functools
import re
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, ParamSpec, TypeVar

from app.core.telemetry import get_meter, get_tracer

if TYPE_CHECKING:
    from opentelemetry.metrics import Counter, Histogram, UpDownCounter
    from opentelemetry.trace import Tracer

# Type variables for generic decorator
P = ParamSpec("P")
R = TypeVar("R")


# =============================================================================
# Lazy Metric Initialization
# =============================================================================
# Metrics are created lazily on first access to ensure they use the configured
# MeterProvider from init_telemetry() rather than the default no-op provider.
# =============================================================================


class _LazyMetrics:
    """Lazy metric initialization to ensure proper provider configuration."""

    _meter = None
    _tracer = None
    _metrics: ClassVar[dict] = {}

    @classmethod
    def _get_meter(cls):
        if cls._meter is None:
            cls._meter = get_meter("pawpoint")
        return cls._meter

    @classmethod
    def _get_tracer(cls) -> "Tracer":
        if cls._tracer is None:
            cls._tracer = get_tracer("pawpoint")
        return cls._tracer

    @classmethod
    def get_counter(cls, name: str, description: str) -> "Counter":
        if name not in cls._metrics:
            cls._metrics[name] = cls._get_meter().create_counter(
                name=name, description=description, unit="1"
            )
        return cls._metrics[name]

    @classmethod
    def get_histogram(cls, name: str, description: str) -> "Histogram":
        if name not in cls._metrics:
            cls._metrics[name] = cls._get_meter().create_histogram(
                name=name, description=description, unit="s"
            )
        return cls._metrics[name]

    @classmethod
    def get_up_down_counter(cls, name: str, description: str) -> "UpDownCounter":
        if name not in cls._metrics:
            cls._metrics[name] = cls._get_meter().create_up_down_counter(
                name=name, description=description, unit="1"
            )
        return cls._metrics[name]


def _get_tracer() -> "Tracer":
    """Get tracer instance (lazily initialized)."""
    return _LazyMetrics._get_tracer()


# =============================================================================
# Metric Accessors (Lazy)
# =============================================================================


def _api_requests_total() -> "Counter":
    return _LazyMetrics.get_counter("pawpoint_api_requests_total", "Total API requests")


def _chat_messages_total() -> "Counter":
    return _LazyMetrics.get_counter(
        "pawpoint_chat_messages_total", "Total chat messages processed"
    )


def _chat_tokens_total() -> "Counter":
    return _LazyMetrics.get_counter(
        "pawpoint_chat_tokens_total", "Total tokens used in chat"
    )


def _db_queries_total() -> "Counter":
    return _LazyMetrics.get_counter(
        "pawpoint_db_queries_total", "Total database queries executed"
    )


def _auth_attempts_total() -> "Counter":
    return _LazyMetrics.get_counter(
        "pawpoint_auth_attempts_total", "Total authentication attempts"
    )


def _api_request_duration_seconds() -> "Histogram":
    return _LazyMetrics.get_histogram(
        "pawpoint_api_request_duration_seconds", "API request duration"
    )


def _chat_response_duration_seconds() -> "Histogram":
    return _LazyMetrics.get_histogram(
        "pawpoint_chat_response_duration_seconds", "Chat response latency"
    )


def _db_query_duration_seconds() -> "Histogram":
    return _LazyMetrics.get_histogram(
        "pawpoint_db_query_duration_seconds", "Database query duration"
    )


def _llm_request_duration_seconds() -> "Histogram":
    return _LazyMetrics.get_histogram(
        "pawpoint_llm_request_duration_seconds", "LLM API request duration"
    )


def _active_websocket_connections() -> "UpDownCounter":
    return _LazyMetrics.get_up_down_counter(
        "pawpoint_active_websocket_connections", "Current active WebSocket connections"
    )


def _active_chat_sessions() -> "UpDownCounter":
    return _LazyMetrics.get_up_down_counter(
        "pawpoint_active_chat_sessions", "Current active chat sessions"
    )


# =============================================================================
# Backwards-compatible module-level accessors
# These are properties that lazily initialize metrics on first access
# =============================================================================


class _MetricProxy:
    """Proxy object that forwards attribute access to lazy metric getter."""

    def __init__(self, getter):
        self._getter = getter

    def add(self, amount, attributes=None):
        return self._getter().add(amount, attributes or {})

    def record(self, value, attributes=None):
        return self._getter().record(value, attributes or {})


# Module-level metric objects (lazy via proxy)
api_requests_total = _MetricProxy(_api_requests_total)
chat_messages_total = _MetricProxy(_chat_messages_total)
chat_tokens_total = _MetricProxy(_chat_tokens_total)
db_queries_total = _MetricProxy(_db_queries_total)
auth_attempts_total = _MetricProxy(_auth_attempts_total)
api_request_duration_seconds = _MetricProxy(_api_request_duration_seconds)
chat_response_duration_seconds = _MetricProxy(_chat_response_duration_seconds)
db_query_duration_seconds = _MetricProxy(_db_query_duration_seconds)
llm_request_duration_seconds = _MetricProxy(_llm_request_duration_seconds)
active_websocket_connections = _MetricProxy(_active_websocket_connections)
active_chat_sessions = _MetricProxy(_active_chat_sessions)


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
        name = (
            span_name
            or f"{getattr(func, '__module__', __name__)}.{getattr(func, '__qualname__', 'unknown')}"
        )

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with _get_tracer().start_as_current_span(name) as span:
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
            with _get_tracer().start_as_current_span(name) as span:
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
    session_id: str,  # kept for API compatibility, not used in metrics to avoid cardinality
    role: str,
    tokens: int = 0,
) -> None:
    """Record a chat message metric.

    Args:
        clinic_id: Clinic identifier
        session_id: Chat session identifier (not included in metrics to avoid cardinality explosion)
        role: Message role (user, assistant, system)
        tokens: Number of tokens used
    """
    # Note: session_id intentionally not included in attributes to prevent
    # high cardinality issues (each session would create new metric series)
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


# =============================================================================
# Session Tracking Helpers
# =============================================================================


def increment_active_chat_sessions(clinic_id: str) -> None:
    """Increment the active chat sessions counter for a clinic.

    Call this when a new chat session is created.

    Args:
        clinic_id: Clinic identifier
    """
    active_chat_sessions.add(1, {"clinic_id": clinic_id})


def decrement_active_chat_sessions(clinic_id: str) -> None:
    """Decrement the active chat sessions counter for a clinic.

    Call this when a chat session ends or is deleted.

    Args:
        clinic_id: Clinic identifier
    """
    active_chat_sessions.add(-1, {"clinic_id": clinic_id})
