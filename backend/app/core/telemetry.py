"""OpenTelemetry instrumentation for PawPoint backend.

Provides:
- Distributed tracing with OTLP export and sampling
- Prometheus metrics endpoint with exemplar support
- Structured logging with trace correlation
- Environment-aware configuration (local vs production)
- Auto-instrumentation for SQLAlchemy, HTTPX, Redis
"""

from typing import TYPE_CHECKING

from loguru import logger
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    SERVICE_NAMESPACE,
    SERVICE_VERSION,
    OsResourceDetector,
    ProcessResourceDetector,
    Resource,
    get_aggregated_resources,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

if TYPE_CHECKING:
    from fastapi import FastAPI

    from app.core.config import Settings


def create_resource(settings: "Settings") -> Resource:
    """Create OpenTelemetry resource with auto-detection.

    Aggregates OS and process metadata with service-specific attributes.
    """
    base_resource = Resource.create(
        {
            SERVICE_NAME: settings.otel_service_name,
            SERVICE_VERSION: settings.app_version,
            DEPLOYMENT_ENVIRONMENT: settings.app_env.value,
            SERVICE_NAMESPACE: "pawpoint",
        }
    )

    # Aggregate with auto-detected resources
    detected_resource = get_aggregated_resources(
        [
            OsResourceDetector(),
            ProcessResourceDetector(),
        ]
    )

    # Merge with base resource (base takes precedence)
    return detected_resource.merge(base_resource)


def init_tracing(
    resource: Resource,
    settings: "Settings",
    otlp_endpoint: str | None = None,
    otlp_headers: dict[str, str] | None = None,
) -> TracerProvider:
    """Initialize tracing with OTLP exporter and sampling.

    Args:
        resource: OpenTelemetry resource describing the service
        settings: Application settings for environment detection
        otlp_endpoint: OTLP collector endpoint (e.g., http://localhost:4317)
        otlp_headers: Headers for authentication (e.g., Grafana Cloud token)

    Returns:
        Configured TracerProvider with sampling
    """
    # 10% sampling in production, 100% in development
    sample_rate = 0.1 if settings.is_production else 1.0
    sampler = ParentBasedTraceIdRatio(sample_rate)

    provider = TracerProvider(resource=resource, sampler=sampler)
    logger.info("Trace sampling rate: {}%", int(sample_rate * 100))

    if otlp_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=otlp_headers or {},
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("OTLP trace exporter configured: {}", otlp_endpoint)

    trace.set_tracer_provider(provider)
    return provider


def init_metrics(
    resource: Resource,
    otlp_endpoint: str | None = None,
    otlp_headers: dict[str, str] | None = None,
    prometheus_enabled: bool = True,
) -> tuple[MeterProvider, PrometheusMetricReader | None]:
    """Initialize metrics with Prometheus and/or OTLP exporters.

    Supports exemplars for trace-to-metrics correlation via DELTA temporality.

    Args:
        resource: OpenTelemetry resource describing the service
        otlp_endpoint: OTLP collector endpoint for metrics
        otlp_headers: Headers for authentication
        prometheus_enabled: Whether to enable Prometheus scrape endpoint

    Returns:
        Tuple of (MeterProvider, PrometheusMetricReader or None)
    """
    readers = []
    prometheus_reader = None

    # Prometheus exporter for /metrics endpoint
    if prometheus_enabled:
        prometheus_reader = PrometheusMetricReader()
        readers.append(prometheus_reader)
        logger.info("Prometheus metrics reader enabled")

    # OTLP exporter for Grafana Cloud / Alloy
    if otlp_endpoint:
        otlp_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=otlp_endpoint,
                headers=otlp_headers or {},
            ),
            export_interval_millis=60000,  # Export every 60 seconds
        )
        readers.append(otlp_reader)
        logger.info("OTLP metrics exporter configured: {}", otlp_endpoint)

    provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(provider)
    return provider, prometheus_reader


def parse_otlp_headers(headers_str: str | None) -> dict[str, str]:
    """Parse OTLP headers from environment variable format.

    Format: "key1=value1,key2=value2"
    """
    if not headers_str:
        return {}

    headers = {}
    for pair in headers_str.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers


def instrument_libraries(settings: "Settings") -> None:
    """Instrument external libraries for automatic tracing.

    Instruments SQLAlchemy, HTTPX, and Redis if available.
    """
    # Instrument SQLAlchemy (database queries)
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        # Check if already instrumented
        if not SQLAlchemyInstrumentor().is_instrumented_by_opentelemetry:
            SQLAlchemyInstrumentor().instrument(
                enable_commenter=True,
                commenter_options={
                    "db_framework": True,
                    "opentelemetry_values": True,
                },
            )
            logger.info("SQLAlchemy instrumentation enabled")
    except ImportError:
        logger.debug("SQLAlchemy instrumentation not available")

    # Instrument HTTPX (HTTP client calls)
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        if not HTTPXClientInstrumentor().is_instrumented_by_opentelemetry:
            HTTPXClientInstrumentor().instrument()
            logger.info("HTTPX instrumentation enabled")
    except ImportError:
        logger.debug("HTTPX instrumentation not available")

    # Instrument Redis (cache operations)
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        if not RedisInstrumentor().is_instrumented_by_opentelemetry:
            RedisInstrumentor().instrument()
            logger.info("Redis instrumentation enabled")
    except ImportError:
        logger.debug("Redis instrumentation not available")


def init_telemetry(app: "FastAPI", settings: "Settings") -> None:
    """Initialize OpenTelemetry instrumentation for FastAPI app.

    Args:
        app: FastAPI application instance
        settings: Application configuration settings
    """
    if not settings.otel_enabled:
        logger.info("OpenTelemetry is disabled")
        return

    logger.info("Initializing OpenTelemetry instrumentation...")

    # Create resource with auto-detection
    resource = create_resource(settings)

    # Parse headers for Grafana Cloud authentication
    otlp_headers = parse_otlp_headers(settings.otel_exporter_otlp_headers)

    # Initialize tracing with sampling
    init_tracing(
        resource=resource,
        settings=settings,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        otlp_headers=otlp_headers,
    )

    # Initialize metrics
    meter_provider, _ = init_metrics(
        resource=resource,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        otlp_headers=otlp_headers,
        prometheus_enabled=settings.prometheus_enabled,
    )

    # Instrument external libraries
    instrument_libraries(settings)

    # Instrument FastAPI with both tracing and metrics
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace.get_tracer_provider(),
        meter_provider=meter_provider,
        excluded_urls="health,metrics",  # Don't trace health/metrics endpoints
    )
    logger.info("FastAPI instrumentation enabled")


def shutdown_telemetry(app: "FastAPI") -> None:
    """Shutdown OpenTelemetry instrumentation cleanly."""
    try:
        FastAPIInstrumentor.uninstrument_app(app)

        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, "shutdown") and callable(tracer_provider.shutdown):
            tracer_provider.shutdown()  # type: ignore[misc]

        meter_provider = metrics.get_meter_provider()
        if hasattr(meter_provider, "shutdown") and callable(meter_provider.shutdown):
            meter_provider.shutdown()  # type: ignore[misc]

        logger.info("OpenTelemetry shutdown complete")
    except Exception as e:
        logger.warning("Error during telemetry shutdown: %s", e)


# Type alias for settings - actual settings class defined in config.py
class TelemetrySettings:
    """Protocol for telemetry settings (actual implementation in config.py)."""

    otel_enabled: bool
    otel_service_name: str
    otel_exporter_otlp_endpoint: str | None
    otel_exporter_otlp_headers: str | None
    prometheus_enabled: bool
    app_version: str
    app_env: str


def get_tracer(name: str = __name__) -> trace.Tracer:
    """Get a tracer instance for creating spans.

    Usage:
        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("my-operation") as span:
            span.set_attribute("key", "value")
            # ... your code
    """
    return trace.get_tracer(name)


def get_meter(name: str = __name__) -> metrics.Meter:
    """Get a meter instance for creating metrics.

    Usage:
        meter = get_meter(__name__)
        counter = meter.create_counter("my_counter", description="My counter")
        counter.add(1, {"label": "value"})
    """
    return metrics.get_meter(name)


def get_current_trace_id() -> str | None:
    """Get the current trace ID for correlation.

    Returns:
        Hex-encoded trace ID or None if no active span.
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, "032x")
    return None


def get_current_span_id() -> str | None:
    """Get the current span ID for correlation.

    Returns:
        Hex-encoded span ID or None if no active span.
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, "016x")
    return None
