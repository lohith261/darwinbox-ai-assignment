"""Global exception handling and structured domain exception contracts."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.schemas.errors import ErrorResponse
from backend.tracing.logging import get_logger


class DarwinError(Exception):
    """Base exception for all Darwin engine errors."""

    def __init__(self, detail: str, error_code: str, status_code: int = 500) -> None:
        super().__init__(detail)
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code


class LLMError(DarwinError):
    """Exception raised when an LLM interaction or router model fails."""

    def __init__(self, detail: str = "LLM gateway error.") -> None:
        super().__init__(detail, "llm_error", 502)


class VectorDatabaseError(DarwinError):
    """Exception raised when ChromaDB, embedding lookup, or document index retrieval fails."""

    def __init__(self, detail: str = "Vector database lookup failure.") -> None:
        super().__init__(detail, "vector_db_error", 500)


class ToolExecutionError(DarwinError):
    """Exception raised when a downstream mock HR integration tool fails."""

    def __init__(self, detail: str = "HR API execution error.") -> None:
        super().__init__(detail, "tool_execution_error", 502)


async def handle_darwin_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle custom Darwin exceptions and log details in a structured format."""
    if not isinstance(exc, DarwinError):
        return await handle_unexpected_error(request, exc)
    logger = get_logger(__name__)
    logger.error(
        "darwin_domain_error",
        error_code=exc.error_code,
        detail=exc.detail,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    payload = ErrorResponse(
        detail=exc.detail,
        error_code=exc.error_code,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


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
    """Handle uncaught exceptions and prevent stack trace leaks to the client."""
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
    app.add_exception_handler(DarwinError, handle_darwin_error)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
