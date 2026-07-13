"""Application factory for the FastAPI service."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.router import api_router
from backend.config.settings import Settings, get_settings
from backend.core.exceptions import register_exception_handlers
from backend.core.middleware import register_middleware
from backend.core.state import ApplicationContainer
from backend.tracing.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure shared resources for the application lifecycle."""
    container = app.state.container
    configure_logging(container.settings.log_level)
    logger = get_logger(__name__)
    logger.info(
        "application_starting",
        app_name=container.settings.app_name,
        environment=container.settings.app_env,
    )
    yield
    logger.info("application_stopping", app_name=container.settings.app_name)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.container = ApplicationContainer(settings=resolved_settings)

    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router)

    return app
