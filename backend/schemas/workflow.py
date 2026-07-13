"""Workflow request and response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class WorkflowInvokeRequest(BaseModel):
    """Request payload for invoking the workflow."""

    user_input: str = Field(
        min_length=1,
        max_length=500,
        description="User request for the workflow.",
    )
    session_id: str | None = Field(
        default=None,
        max_length=100,
        pattern=r"^[a-zA-Z0-9\-_]+$",
        description="Optional session identifier used for LangGraph thread persistence.",
    )


class WorkflowInvokeResponse(BaseModel):
    """Response returned after a workflow invocation."""

    session_id: str
    route_decision: dict[str, Any]
    executed_agents: list[str]
    messages: list[dict[str, Any]]
    graph_visualization: str
    policy_result: dict[str, Any] | None = None
    action_result: dict[str, Any] | None = None
    employee_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    naive_cost: float | None = None
    optimized_cost: float | None = None
    percentage_reduction: float | None = None
    latency_sec: float | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class WorkflowSessionResponse(BaseModel):
    """Response for session state inspection."""

    session_id: str
    next_nodes: list[str]
    executed_agents: list[str]
    route_decision: dict[str, Any] | None = None
    messages: list[dict[str, Any]]
    employee_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class GraphVisualizationResponse(BaseModel):
    """Graph visualization payload."""

    mermaid: str
