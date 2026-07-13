"""Unit and integration tests for deterministic routing and cost optimization."""

import uuid

from backend.agents.action import ActionAgent
from backend.agents.policy import PolicyAgent
from backend.agents.supervisor import SupervisorAgent
from backend.agents.workflow import WorkflowGraph
from backend.config.settings import get_settings
from backend.rag.models import RetrievalHit
from backend.schemas.workflow import WorkflowInvokeRequest
from backend.services.workflow import WorkflowService


class MockRetriever:
    """Mock retriever that returns empty hits."""

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        return []


def test_deterministic_routing_bypasses_llm() -> None:
    settings = get_settings()
    settings.openai_api_key = "mock-openai-key"

    supervisor = SupervisorAgent(settings=settings)
    policy = PolicyAgent(retriever=MockRetriever())
    action = ActionAgent()
    workflow_graph = WorkflowGraph(
        supervisor_agent=supervisor, policy_agent=policy, action_agent=action
    )
    service = WorkflowService(workflow_graph=workflow_graph)

    # 1. Deterministic request: should bypass LLM (100% cost reduction)
    req_det = WorkflowInvokeRequest(
        user_input="Check my leave balance for employee EMP-123",
        session_id=str(uuid.uuid4()),
    )
    res_det = service.invoke(request=req_det)

    assert res_det.naive_cost is not None
    assert res_det.naive_cost > 0.0
    assert res_det.optimized_cost == 0.0
    assert res_det.percentage_reduction == 100.0
    assert "Bypassed LLM" in res_det.route_decision["rationale"]

    # 2. Non-deterministic request: should route via LLM (0% cost reduction)
    req_non_det = WorkflowInvokeRequest(
        user_input="What is the notice period required for remote work?",
        session_id=str(uuid.uuid4()),
    )
    res_non_det = service.invoke(request=req_non_det)

    assert res_non_det.naive_cost is not None
    assert res_non_det.naive_cost > 0.0
    assert res_non_det.optimized_cost == res_non_det.naive_cost
    assert res_non_det.percentage_reduction == 0.0
