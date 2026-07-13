"""Workflow execution endpoints."""

from fastapi import APIRouter, Depends, Path

from backend.dependencies import get_workflow_service
from backend.schemas.workflow import (
    GraphVisualizationResponse,
    WorkflowInvokeRequest,
    WorkflowInvokeResponse,
    WorkflowSessionResponse,
)
from backend.services.workflow import WorkflowService

router = APIRouter(prefix="/api/v1/workflows", tags=["workflow"])


@router.post("/invoke", response_model=WorkflowInvokeResponse)
async def invoke_workflow(
    request: WorkflowInvokeRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowInvokeResponse:
    """Execute the supervisor-driven workflow graph."""
    return workflow_service.invoke(request)


@router.get("/graph", response_model=GraphVisualizationResponse)
async def get_workflow_graph(
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> GraphVisualizationResponse:
    """Return the workflow graph visualization."""
    return workflow_service.graph_visualization()


@router.get("/sessions/{session_id}", response_model=WorkflowSessionResponse)
async def get_workflow_session(
    session_id: str = Path(
        ...,
        pattern=r"^[a-zA-Z0-9\-_]+$",
        max_length=100,
        description="Persisted session identifier.",
    ),
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowSessionResponse:
    """Return the current persisted state for a workflow session."""
    return workflow_service.get_session(session_id)
