"""Integration tests for LangGraph conversation memory."""

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


def test_workflow_memory_persistence() -> None:
    settings = get_settings()
    # Ensure api key is configured so supervisor decides without throwing
    # (though it falls back anyway)
    settings.openai_api_key = "mock-openai-key"

    supervisor = SupervisorAgent(settings=settings)
    policy = PolicyAgent(retriever=MockRetriever())
    action = ActionAgent()
    workflow_graph = WorkflowGraph(
        supervisor_agent=supervisor, policy_agent=policy, action_agent=action
    )
    service = WorkflowService(workflow_graph=workflow_graph)

    session_id = str(uuid.uuid4())

    # Turn 1: Provide full details (employee_id, dates)
    req1 = WorkflowInvokeRequest(
        user_input="Apply sick leave for employee EMP-999 from 2026-08-01 to 2026-08-05",
        session_id=session_id,
    )
    res_turn1 = service.invoke(request=req1)

    assert res_turn1.employee_id == "EMP-999"
    assert res_turn1.start_date == "2026-08-01"
    assert res_turn1.end_date == "2026-08-05"
    assert res_turn1.action_result is not None
    assert res_turn1.action_result["tool"] == "apply_leave"
    assert "Applied for leave" in res_turn1.action_result["summary"]

    # Turn 2: Follow-up query requesting changes (no dates or employee ID in the text)
    req2 = WorkflowInvokeRequest(
        user_input="Actually, change that to casual leave",
        session_id=session_id,
    )
    res_turn2 = service.invoke(request=req2)

    # Memory check: employee_id and dates should be remembered from Turn 1!
    assert res_turn2.employee_id == "EMP-999"
    assert res_turn2.start_date == "2026-08-01"
    assert res_turn2.end_date == "2026-08-05"
    assert res_turn2.action_result is not None
    assert res_turn2.action_result["tool"] == "apply_leave"
    assert res_turn2.action_result["output"]["leave_type"] == "casual"
    assert "casual" in res_turn2.action_result["summary"].lower()


def test_workflow_memory_history_preservation() -> None:
    settings = get_settings()
    settings.openai_api_key = "mock-openai-key"

    supervisor = SupervisorAgent(settings=settings)
    policy = PolicyAgent(retriever=MockRetriever())
    action = ActionAgent()
    workflow_graph = WorkflowGraph(
        supervisor_agent=supervisor, policy_agent=policy, action_agent=action
    )
    service = WorkflowService(workflow_graph=workflow_graph)

    session_id = str(uuid.uuid4())

    # Turn 1
    req1 = WorkflowInvokeRequest(
        user_input="How many days of sick leave do I get?",
        session_id=session_id,
    )
    service.invoke(request=req1)

    # Turn 2
    req2 = WorkflowInvokeRequest(
        user_input="Apply sick leave for EMP-555",
        session_id=session_id,
    )
    res2 = service.invoke(request=req2)

    # Total messages in history should be 4:
    # Turn 1: 1 HumanMessage + 1 AIMessage (from supervisor or agent)
    # Turn 2: 1 HumanMessage + 1 AIMessage (appended to history)
    # The first message in the session history should be the user's first query
    assert len(res2.messages) >= 4
    assert "sick leave do I get" in res2.messages[0]["content"]
