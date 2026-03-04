"""Request logging middleware."""

import time
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request start/end with timing and add X-Request-ID header."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health/metrics endpoints
        if request.url.path in ("/health", "/metrics", "/"):
            return await call_next(request)

        request_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "Request started: {} {} client={}",
            request.method,
            request.url.path,
            client_ip,
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Request failed: {} {} duration_ms={:.1f}",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Request completed: {} {} status={} duration_ms={:.1f}",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response
