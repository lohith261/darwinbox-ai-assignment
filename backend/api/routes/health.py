"""Health and system endpoints."""

from fastapi import APIRouter, Depends

from backend.dependencies import get_application_service
from backend.schemas.health import HealthResponse
from backend.services.application import ApplicationService

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    application_service: ApplicationService = Depends(get_application_service),
) -> HealthResponse:
    """Return service health information."""
    return application_service.health()
