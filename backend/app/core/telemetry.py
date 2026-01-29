"""OpenTelemetry instrumentation for PawPoint backend.

Provides:
- Distributed tracing with OTLP export
- Prometheus metrics endpoint
- Structured logging with trace correlation
- Environment-aware configuration (local vs Grafana Cloud)
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
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

if TYPE_CHECKING:
    from fastapi import FastAPI

    from app.core.config import Settings


def create_resource(
    service_name: str, service_version: str, environment: str
) -> Resource:
    """Create OpenTelemetry resource with service metadata."""
    return Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "deployment.environment": environment,
            "service.namespace": "pawpoint",
        }
    )


def init_tracing(
    resource: Resource,
    otlp_endpoint: str | None = None,
    otlp_headers: dict[str, str] | None = None,
) -> TracerProvider:
    """Initialize tracing with OTLP exporter.

    Args:
        resource: OpenTelemetry resource describing the service
        otlp_endpoint: OTLP collector endpoint (e.g., http://localhost:4317)
        otlp_headers: Headers for authentication (e.g., Grafana Cloud token)

    Returns:
        Configured TracerProvider
    """
    provider = TracerProvider(resource=resource)

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

    # Create resource with service metadata
    resource = create_resource(
        service_name=settings.otel_service_name,
        service_version=settings.app_version,
        environment=settings.app_env,
    )

    # Parse headers for Grafana Cloud authentication
    otlp_headers = parse_otlp_headers(settings.otel_exporter_otlp_headers)

    # Initialize tracing
    init_tracing(
        resource=resource,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        otlp_headers=otlp_headers,
    )

    # Initialize metrics
    init_metrics(
        resource=resource,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        otlp_headers=otlp_headers,
        prometheus_enabled=settings.prometheus_enabled,
    )

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(
        app,
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
