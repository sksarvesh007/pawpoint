"""
Voice-Specific Telemetry for LiveKit Agent

Tracks metrics for STT, LLM, and TTS latency, call duration, and tool execution.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.metrics import Counter, Histogram

logger = logging.getLogger(__name__)

# Get tracer and meter
tracer = trace.get_tracer("livekit-agent")
meter = metrics.get_meter("livekit-agent")

# Metrics
call_duration: Histogram = meter.create_histogram(
    name="voice.call.duration",
    description="Duration of voice calls in seconds",
    unit="s",
)

call_count: Counter = meter.create_counter(
    name="voice.call.count",
    description="Total number of voice calls",
    unit="1",
)

stt_latency: Histogram = meter.create_histogram(
    name="voice.stt.latency",
    description="Speech-to-text processing latency",
    unit="ms",
)

llm_latency: Histogram = meter.create_histogram(
    name="voice.llm.latency",
    description="LLM response generation latency",
    unit="ms",
)

tts_latency: Histogram = meter.create_histogram(
    name="voice.tts.latency",
    description="Text-to-speech synthesis latency",
    unit="ms",
)

tool_execution: Histogram = meter.create_histogram(
    name="voice.tool.execution",
    description="Tool execution time",
    unit="ms",
)

errors_count: Counter = meter.create_counter(
    name="voice.errors.count",
    description="Total number of errors during voice calls",
    unit="1",
)


def record_call_start(clinic_id: str, channel: str) -> None:
    """Record start of a voice call."""
    call_count.add(1, {"clinic_id": clinic_id, "channel": channel})


def record_call_end(clinic_id: str, channel: str, duration_seconds: float) -> None:
    """Record end of a voice call with duration."""
    call_duration.record(
        duration_seconds,
        {"clinic_id": clinic_id, "channel": channel},
    )


def record_stt_latency_ms(latency_ms: float) -> None:
    """Record speech-to-text latency."""
    stt_latency.record(latency_ms)


def record_llm_latency_ms(latency_ms: float, model: str) -> None:
    """Record LLM response latency."""
    llm_latency.record(latency_ms, {"model": model})


def record_tts_latency_ms(latency_ms: float) -> None:
    """Record text-to-speech latency."""
    tts_latency.record(latency_ms)


def record_tool_execution_ms(tool_name: str, latency_ms: float, success: bool) -> None:
    """Record tool execution time."""
    tool_execution.record(
        latency_ms,
        {"tool": tool_name, "success": str(success).lower()},
    )


def record_error(error_type: str, source: str) -> None:
    """Record an error occurrence."""
    errors_count.add(1, {"error_type": error_type, "source": source})


@asynccontextmanager
async def traced_operation(name: str, attributes: dict[str, Any] | None = None):
    """Context manager for tracing async operations."""
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        try:
            yield span
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


class LatencyTimer:
    """Simple timer for measuring operation latency."""

    def __init__(self) -> None:
        self.start_time: float = 0
        self.end_time: float = 0

    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer and return elapsed milliseconds."""
        self.end_time = time.perf_counter()
        return (self.end_time - self.start_time) * 1000

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.end_time == 0:
            return (time.perf_counter() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000
