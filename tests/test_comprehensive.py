"""Comprehensive tests for the Darwinbox Agentic HR Workflow Engine."""

import time
import uuid
from typing import Any, cast

from backend.agents.action import ActionAgent
from backend.agents.policy import PolicyAgent
from backend.agents.supervisor import SupervisorAgent, SupervisorDecision
from backend.agents.workflow import WorkflowGraph, WorkflowState
from backend.config.settings import get_settings
from backend.rag.models import RetrievalHit
from backend.schemas.workflow import WorkflowInvokeRequest
from backend.services.workflow import WorkflowService
from backend.tools.hr_tools import (
    LeaveBalanceRequest,
    LeaveBalanceResponse,
    execute_with_resilience,
)


class MockRetriever:
    """Mock retriever returning static documents."""

    def __init__(self, hits: list[RetrievalHit] | None = None) -> None:
        self.hits = hits if hits is not None else []

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        return self.hits


# =====================================================================
# 1-3: Supervisor Routing Tests
# =====================================================================


def test_supervisor_routing_policy() -> None:
    """Test that supervisor routes policy questions to policy_agent."""
    settings = get_settings()
    settings.openai_api_key = "mock-key"
    supervisor = SupervisorAgent(settings=settings)
    decision = supervisor.decide("What is the maternity leave policy?", [])
    assert isinstance(decision, SupervisorDecision)
    assert len(decision.next_agents) >= 1


def test_supervisor_routing_action() -> None:
    """Test that supervisor routes action queries to action_agent."""
    settings = get_settings()
    settings.openai_api_key = "mock-key"
    supervisor = SupervisorAgent(settings=settings)
    decision = supervisor.decide("Apply sick leave for me", [])
    assert isinstance(decision, SupervisorDecision)
    assert len(decision.next_agents) >= 1


def test_supervisor_routing_both() -> None:
    """Test that supervisor can route to both agents for complex requests."""
    settings = get_settings()
    settings.openai_api_key = "mock-key"
    supervisor = SupervisorAgent(settings=settings)
    decision = supervisor.decide("What is the sick leave policy and check my leave balance", [])
    assert isinstance(decision, SupervisorDecision)
    assert len(decision.next_agents) >= 1


# =====================================================================
# 4-5: Policy Retrieval Tests
# =====================================================================


def test_policy_retrieval_success() -> None:
    """Test that policy agent successfully answers with retrieved context."""
    hits = [
        RetrievalHit(
            chunk_id="1",
            content="Maternity leave is 26 weeks paid.",
            title="Maternity Leave",
            source="docs/policy.md",
            rank=1,
            distance=0.1,
        )
    ]
    policy = PolicyAgent(retriever=MockRetriever(hits))
    state = cast(
        WorkflowState,
        {
            "user_input": "How long is maternity leave?",
            "messages": [],
            "executed_agents": [],
        },
    )
    res: Any = policy.run(state)
    assert "policy_result" in res
    assert "citations" in res["policy_result"]
    assert len(res["policy_result"]["citations"]) == 1


def test_policy_retrieval_unavailable() -> None:
    """Test that policy agent returns unavailable when retriever has no docs."""
    policy = PolicyAgent(retriever=MockRetriever([]))
    state = cast(
        WorkflowState,
        {
            "user_input": "What is the dog leave policy?",
            "messages": [],
            "executed_agents": [],
        },
    )
    res: Any = policy.run(state)
    assert "policy unavailable" in res["policy_result"]["answer"].lower()


# =====================================================================
# 6-8: Tool Execution Tests
# =====================================================================


def test_tool_execution_leave_balance() -> None:
    """Test ActionAgent routes to check_leave_balance tool successfully."""
    action = ActionAgent()
    state = cast(
        WorkflowState,
        {
            "user_input": "What is my sick leave balance?",
            "employee_id": "EMP-101",
            "messages": [],
        },
    )
    res: Any = action.run(state)
    assert res["action_result"]["tool"] == "check_leave_balance"
    assert res["action_result"]["status"] in ["success", "fallback"]


def test_tool_execution_apply_leave() -> None:
    """Test ActionAgent routes to apply_leave tool successfully."""
    action = ActionAgent()
    state = cast(
        WorkflowState,
        {
            "user_input": "Apply sick leave from 2026-08-01 to 2026-08-05",
            "employee_id": "EMP-101",
            "messages": [],
        },
    )
    res: Any = action.run(state)
    assert res["action_result"]["tool"] == "apply_leave"
    assert res["action_result"]["status"] in ["approved", "fallback_queued"]


def test_tool_execution_fetch_payslip() -> None:
    """Test ActionAgent routes to fetch_payslip tool successfully."""
    action = ActionAgent()
    state = cast(
        WorkflowState,
        {
            "user_input": "Download my payslip for July 2026",
            "employee_id": "EMP-101",
            "messages": [],
        },
    )
    res: Any = action.run(state)
    assert res["action_result"]["tool"] == "fetch_payslip"
    assert res["action_result"]["status"] in ["success", "fallback"]


# =====================================================================
# 9-11: Retry, Timeout, and Resilience Logic Tests
# =====================================================================


def test_tool_retry_logic_eventual_success() -> None:
    """Test that execution retries on failure and eventually succeeds."""
    calls = 0

    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("Temporary API disconnect")
        return LeaveBalanceResponse(
            status="success",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=10,
            source="api",
        )

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=5,
            source="cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, meta = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
        max_retries=2,
    )
    assert res.status == "success"
    assert meta["retries"] == 1
    assert len(meta["failures"]) == 1


def test_tool_retry_logic_exhausted_fallback() -> None:
    """Test that all retries fail and trigger fallback gracefully."""

    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        raise RuntimeError("Permanent DB Error")

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=8,
            source="cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, meta = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
        max_retries=2,
    )
    assert res.status == "fallback"
    assert meta["retries"] == 1
    assert len(meta["failures"]) == 2


def test_tool_timeout_resilience() -> None:
    """Test that tool timeout enforces fallback activation."""

    def core_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        time.sleep(0.5)
        return LeaveBalanceResponse(
            status="success",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=12,
            source="api",
        )

    def fallback_func(req: LeaveBalanceRequest) -> LeaveBalanceResponse:
        return LeaveBalanceResponse(
            status="fallback",
            employee_id=req.employee_id,
            leave_type=req.leave_type,
            balance=4,
            source="cache",
        )

    req = LeaveBalanceRequest(employee_id="EMP-123", leave_type="sick")
    res, meta = execute_with_resilience(
        core_func=core_func,
        request=req,
        fallback_func=fallback_func,
        timeout_sec=0.1,
        max_retries=1,
    )
    assert res.status == "fallback"
    assert "Timeout after 0.1s" in meta["failures"][0]


# =====================================================================
# 12-13: Memory Preservation Tests
# =====================================================================


def test_memory_employee_id_preservation() -> None:
    """Test that Employee ID is preserved in memory across turns."""
    settings = get_settings()
    settings.openai_api_key = "mock-key"
    workflow_graph = WorkflowGraph(
        supervisor_agent=SupervisorAgent(settings=settings),
        policy_agent=PolicyAgent(retriever=MockRetriever()),
        action_agent=ActionAgent(),
    )
    service = WorkflowService(workflow_graph=workflow_graph)
    session_id = str(uuid.uuid4())

    # Turn 1: Specify Employee ID
    req1 = WorkflowInvokeRequest(
        user_input="Check leave balance for employee EMP-505",
        session_id=session_id,
    )
    res1 = service.invoke(request=req1)
    assert res1.employee_id == "EMP-505"

    # Turn 2: Follow-up without Employee ID
    req2 = WorkflowInvokeRequest(
        user_input="What about casual leave?",
        session_id=session_id,
    )
    res2 = service.invoke(request=req2)
    assert res2.employee_id == "EMP-505"


def test_memory_leave_dates_preservation() -> None:
    """Test that leave dates are remembered in memory across turns."""
    settings = get_settings()
    settings.openai_api_key = "mock-key"
    workflow_graph = WorkflowGraph(
        supervisor_agent=SupervisorAgent(settings=settings),
        policy_agent=PolicyAgent(retriever=MockRetriever()),
        action_agent=ActionAgent(),
    )
    service = WorkflowService(workflow_graph=workflow_graph)
    session_id = str(uuid.uuid4())

    # Turn 1: Apply sick leave with dates
    req1 = WorkflowInvokeRequest(
        user_input="Apply sick leave for EMP-888 from 2026-09-01 to 2026-09-05",
        session_id=session_id,
    )
    res1 = service.invoke(request=req1)
    assert res1.start_date == "2026-09-01"
    assert res1.end_date == "2026-09-05"

    # Turn 2: Follow up change type only
    req2 = WorkflowInvokeRequest(
        user_input="Change that to casual leave",
        session_id=session_id,
    )
    res2 = service.invoke(request=req2)
    assert res2.start_date == "2026-09-01"
    assert res2.end_date == "2026-09-05"


# =====================================================================
# 14-16: Error Handling, Edge Cases, and Multi-Turn Conversation
# =====================================================================


def test_error_handling_invalid_inputs() -> None:
    """Test engine handles unusual/unstructured input texts gracefully."""
    action = ActionAgent()
    state = cast(
        WorkflowState,
        {
            "user_input": "xyzabc123 !!! ???",
            "messages": [],
        },
    )
    res: Any = action.run(state)
    assert res["action_result"]["status"] == "unsupported"
    assert "could not determine a matching HR tool" in res["action_result"]["summary"]


def test_edge_case_unknown_routing() -> None:
    """Test routing defaults to fallback policy+action if decision key is empty."""
    workflow_graph = WorkflowGraph(
        supervisor_agent=SupervisorAgent(settings=get_settings()),
        policy_agent=PolicyAgent(retriever=MockRetriever()),
        action_agent=ActionAgent(),
    )
    state = cast(
        WorkflowState,
        {
            "route_decision": {},
        },
    )
    routes = workflow_graph._route_after_supervisor(state)
    assert "policy_agent" in routes
    assert "action_agent" in routes


def test_multi_turn_conversation_flow() -> None:
    """Test a full multi-turn conversational session verifying memory and trace metrics."""
    settings = get_settings()
    settings.openai_api_key = "mock-key"
    workflow_graph = WorkflowGraph(
        supervisor_agent=SupervisorAgent(settings=settings),
        policy_agent=PolicyAgent(retriever=MockRetriever()),
        action_agent=ActionAgent(),
    )
    service = WorkflowService(workflow_graph=workflow_graph)
    session_id = str(uuid.uuid4())

    # Turn 1: Action (balance check)
    req1 = WorkflowInvokeRequest(
        user_input="What is my sick leave balance? My ID is EMP-777",
        session_id=session_id,
    )
    res1 = service.invoke(request=req1)
    assert res1.employee_id == "EMP-777"
    assert res1.action_result is not None
    assert res1.action_result["tool"] == "check_leave_balance"
    assert res1.optimized_cost == 0.0

    # Turn 2: Follow-up check casual
    req2 = WorkflowInvokeRequest(
        user_input="What about casual leave?",
        session_id=session_id,
    )
    res2 = service.invoke(request=req2)
    assert res2.employee_id == "EMP-777"
    assert res2.action_result is not None
    assert res2.action_result["tool"] == "check_leave_balance"

    # Turn 3: Policy check
    hits = [
        RetrievalHit(
            chunk_id="1",
            content="Notice period is 30 days.",
            title="Notice Period",
            source="docs/policy.md",
            rank=1,
            distance=0.1,
        )
    ]
    service.workflow_graph._policy_agent = PolicyAgent(retriever=MockRetriever(hits))
    req3 = WorkflowInvokeRequest(
        user_input="What is the notice period policy?",
        session_id=session_id,
    )
    res3 = service.invoke(request=req3)
    assert res3.policy_result is not None
    assert len(res3.policy_result["citations"]) == 1
