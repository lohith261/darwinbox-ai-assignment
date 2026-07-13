"""Root API router."""

from fastapi import APIRouter

from backend.api.routes.health import router as health_router
from backend.api.routes.workflows import router as workflow_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(workflow_router)
