"""Application middleware registration."""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response

from backend.tracing.logging import get_logger

logger = get_logger(__name__)


async def request_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach request metadata and timing information using structlog contextvars."""
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    correlation_id = request.headers.get("x-correlation-id", request_id)
    request.state.request_id = request_id

    # Bind thread-local context variables for consistent request/correlation tracing
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        correlation_id=correlation_id,
    )

    started_at = time.perf_counter()
    logger.info(
        "request_started",
        path=request.url.path,
        method=request.method,
    )

    response = await call_next(request)

    process_time_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)

    logger.info(
        "request_completed",
        status_code=response.status_code,
        process_time_ms=process_time_ms,
    )
    return response


def register_middleware(app: FastAPI) -> None:
    """Register HTTP middleware."""
    app.middleware("http")(request_context_middleware)
