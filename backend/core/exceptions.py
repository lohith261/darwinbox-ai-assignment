"""Global exception handling."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.schemas.errors import ErrorResponse
from backend.tracing.logging import get_logger


async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle FastAPI validation errors with a stable response contract."""
    logger = get_logger(__name__)
    logger.warning(
        "request_validation_failed",
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown"),
        errors=exc.errors(),
    )
    payload = ErrorResponse(
        detail="Request validation failed.",
        error_code="request_validation_error",
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content=payload.model_dump())


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger = get_logger(__name__)
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown"),
        error=str(exc),
    )
    payload = ErrorResponse(
        detail="An unexpected error occurred.",
        error_code="internal_server_error",
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=payload.model_dump())


async def handle_validation_exception(request: Request, exc: Exception) -> JSONResponse:
    """Adapter matching Starlette's exception handler signature."""
    if not isinstance(exc, RequestValidationError):
        return await handle_unexpected_error(request, exc)
    return await handle_validation_error(request, exc)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
