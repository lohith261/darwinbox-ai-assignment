"""Dependency injection helpers."""

from typing import cast

from fastapi import Request

from backend.core.state import ApplicationContainer
from backend.services.application import ApplicationService
from backend.services.workflow import WorkflowService


def get_container(request: Request) -> ApplicationContainer:
    """Return the shared application container."""
    return cast(ApplicationContainer, request.app.state.container)


def get_application_service(request: Request) -> ApplicationService:
    """Resolve the application service from the container."""
    container = get_container(request)
    return container.application_service


def get_workflow_service(request: Request) -> WorkflowService:
    """Resolve the shared workflow service from the container."""
    container = get_container(request)
    return container.workflow_service
