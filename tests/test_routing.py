"""Comprehensive routing tests for the Darwin Supervisor.

Tests cover:
  - Deterministic bypass routing for action-only queries
  - Deterministic bypass routing for policy-only queries
  - Mixed queries (not matched deterministically — defer to LLM)
  - Supervisor LLM routing via the SupervisorAgent
  - Full graph integration (deterministic paths)
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest

from backend.agents.supervisor import SUPERVISOR_SYSTEM_PROMPT, SupervisorAgent, SupervisorDecision
from backend.agents.workflow import WorkflowGraph


# =========================================================================
# Helpers
# =========================================================================


class FakeSettings:
    """Minimal settings stub that never initialises an actual LLM client."""

    openai_api_key: str = ""
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"


class FakePolicyRetriever:
    """Stub retriever that returns empty hits and mimics PolicyAgent.run()."""

    name: str = "policy_agent"

    def retrieve(self, query: str, top_k: int = 4) -> list[Any]:
        return []

    def run(self, state: Any) -> dict[str, object]:
        """Return a minimal 'unavailable' policy result so the graph node runs cleanly."""
        return {
            "messages": [],
            "executed_agents": [self.name],
            "policy_result": {
                "status": "unavailable",
                "answer": "Policy unavailable: no relevant context found.",
                "citations": [],
            },
        }


class FakeActionAgent:
    """Stub action agent that records the user input it received."""

    name: str = "action_agent"
    last_input: str = ""

    def run(self, state: Any) -> dict[str, object]:
        user_input = state.get("user_input", "") if isinstance(state, dict) else str(state)
        self.last_input = user_input
        return {
            "messages": [],
            "executed_agents": [self.name],
            "action_result": {"status": "success", "summary": "fake"},
        }


def deterministic_routing_for(query: str) -> tuple[bool, list[str], str]:
    """Convenience: build a minimal WorkflowGraph and call _is_deterministic."""
    fake_settings = FakeSettings()
    fake_supervisor = SupervisorAgent(settings=fake_settings)  # type: ignore[arg-type]
    fake_policy = FakePolicyRetriever()
    fake_action = FakeActionAgent()
    graph = WorkflowGraph(
        supervisor_agent=fake_supervisor,
        policy_agent=fake_policy,  # type: ignore[arg-type]
        action_agent=fake_action,  # type: ignore[arg-type]
    )
    return graph._is_deterministic(query)


# =========================================================================
# 1. Deterministic Bypass — Action-only Queries
# =========================================================================


class TestDeterministicActionRouting:
    """Queries that should bypass the LLM and go directly to action_agent."""

    @pytest.mark.parametrize(
        "query",
        [
            "What is my leave balance?",
            "check my remaining leave",
            "how many days of leave do I have left",
            "Show my sick leave balance",
            "What's my casual leave balance?",
            "check balance",
        ],
    )
    def test_leave_balance_patterns(self, query: str) -> None:
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is True, f"Expected deterministic=True for: {query!r}"
        assert agents == ["action_agent"], f"Expected action_agent for: {query!r}"
        assert "Bypassed LLM" in rationale

    @pytest.mark.parametrize(
        "query",
        [
            "Download my payslip",
            "Fetch my salary for July 2026",
            "Show me my pay slip",
        ],
    )
    def test_payslip_patterns(self, query: str) -> None:
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is True, f"Expected deterministic=True for: {query!r}"
        assert agents == ["action_agent"], f"Expected action_agent for: {query!r}"
        assert "Bypassed LLM" in rationale

    @pytest.mark.parametrize(
        "query",
        [
            "Apply for 2 days casual leave from 2026-07-20 to 2026-07-21",
            "Request sick leave for tomorrow",
            "Take earned leave next week",
        ],
    )
    def test_apply_leave_patterns(self, query: str) -> None:
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is True, f"Expected deterministic=True for: {query!r}"
        assert agents == ["action_agent"], f"Expected action_agent for: {query!r}"
        assert "Bypassed LLM" in rationale


# =========================================================================
# 2. Deterministic Bypass — Policy-only Queries
# =========================================================================


class TestDeterministicPolicyRouting:
    """Queries that should bypass the LLM and go directly to policy_agent."""

    @pytest.mark.parametrize(
        "query",
        [
            "What is the notice period policy?",
            "Tell me about the work from home policy",
            "What does the remote work policy say?",
            "What is the sick leave policy?",
            "Explain the casual leave policy",
            "What is the maternity leave policy?",
            "What does the policy say about earned leave?",
            "What is the attendance policy?",
            "Tell me about the payroll policy",
            "What is the paternity leave policy?",
            "What is the policy on casual leave?",
            "What does the policy say about notice period?",
        ],
    )
    def test_policy_patterns(self, query: str) -> None:
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is True, f"Expected deterministic=True for: {query!r}"
        assert agents == ["policy_agent"], f"Expected policy_agent for: {query!r}"
        assert "Bypassed LLM" in rationale

    @pytest.mark.parametrize(
        "query",
        [
            "Can casual leave be carried forward?",
            "How many sick days am I eligible for?",
            "How many days of sick leave can I take?",  # 'sick' alone isn't a policy keyword
        ],
    )
    def test_policy_adjacent_queries(self, query: str) -> None:
        """Queries about policy content but without explicit 'policy' keyword
        should NOT be matched deterministically (they flow to the LLM)."""
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is False, f"Expected deterministic=False for: {query!r}"


# =========================================================================
# 3. Policy queries that look like action queries — MUST route to policy
# =========================================================================


class TestPolicyVsActionDisambiguation:
    """Queries that contain action-like keywords but are clearly about policy."""

    @pytest.mark.parametrize(
        "query",
        [
            "What is the leave balance policy?",
            "Tell me about the payslip policy",
            "What does the policy on salary deductions say?",
            "What is the policy on applying for leave?",
        ],
    )
    def test_policy_queries_with_action_overlap(self, query: str) -> None:
        """These queries contain action keywords ('balance', 'payslip', etc.)
        AND strong policy signals ('policy', 'what does the policy say').
        The strong policy signal overrides the action match, so they are NOT
        matched deterministically and flow to the LLM for correct disambiguation."""
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is False, (
            f"Expected deterministic=False for mixed-signal query: {query!r}. "
            f"Got agents={agents}. These should flow to the LLM for disambiguation."
        )


# =========================================================================
# 4. Mixed Queries — NOT matched deterministically
# =========================================================================


class TestMixedQueryRouting:
    """Queries that combine policy + action intent must NOT match deterministic
    bypass — they should be deferred to the LLM supervisor."""

    @pytest.mark.parametrize(
        "query",
        [
            "Tell me about WFH policy and check my leave balance",
            "What is the notice period and apply for sick leave",
        ],
    )
    def test_mixed_queries_are_not_deterministic(self, query: str) -> None:
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is False, (
            f"Expected deterministic=False for mixed query: {query!r}. "
            f"Mixed queries should go to LLM, not bypass."
        )


# =========================================================================
# 5. Gibberish / Unsupported / Ambiguous — NOT matched deterministically
# =========================================================================


class TestUnsupportedQueries:
    """Queries that don't fit any pattern should NOT match deterministic."""

    @pytest.mark.parametrize(
        "query",
        [
            "asdfghjkl",
            "Hello, how are you?",
            "What is the meaning of life?",
            "",
        ],
    )
    def test_gibberish_or_off_topic(self, query: str) -> None:
        is_det, agents, rationale = deterministic_routing_for(query)
        assert is_det is False, f"Expected deterministic=False for: {query!r}"


# =========================================================================
# 6. SupervisorAgent Decision (LLM path)
# =========================================================================


class TestSupervisorAgentDecision:
    """Verify that the SupervisorAgent's decide() method works correctly
    with a real (or mocked) LLM route."""

    def test_default_decision_when_no_api_key(self) -> None:
        """When no API key is configured, the supervisor should fall back to
        a safe default that routes to both agents."""
        fake_settings = FakeSettings()
        agent = SupervisorAgent(settings=fake_settings)  # type: ignore[arg-type]
        decision = agent.decide("What is the notice period?")
        assert isinstance(decision, SupervisorDecision)
        assert "policy_agent" in decision.next_agents
        assert "action_agent" in decision.next_agents
        assert "OpenAI API key is not configured" in decision.rationale


# =========================================================================
# 7. _route_after_supervisor  (edge resolution)
# =========================================================================


class TestRouteAfterSupervisor:
    """Tests for the conditional edge function that translates the
    SupervisorDecision into actual LangGraph edge destinations."""

    def _make_state(self, next_agents: list[str]) -> dict[str, Any]:
        return {
            "route_decision": {"next_agents": next_agents, "rationale": "test"},
            "messages": [],
            "user_input": "test",
            "executed_agents": [],
        }

    def test_route_to_policy_only(self) -> None:
        fake_settings = FakeSettings()
        graph = WorkflowGraph(
            supervisor_agent=SupervisorAgent(settings=fake_settings),  # type: ignore[arg-type]
            policy_agent=FakePolicyRetriever(),  # type: ignore[arg-type]
            action_agent=FakeActionAgent(),  # type: ignore[arg-type]
        )
        result = graph._route_after_supervisor(self._make_state(["policy_agent"]))
        assert result == ["policy_agent"]

    def test_route_to_action_only(self) -> None:
        fake_settings = FakeSettings()
        graph = WorkflowGraph(
            supervisor_agent=SupervisorAgent(settings=fake_settings),  # type: ignore[arg-type]
            policy_agent=FakePolicyRetriever(),  # type: ignore[arg-type]
            action_agent=FakeActionAgent(),  # type: ignore[arg-type]
        )
        result = graph._route_after_supervisor(self._make_state(["action_agent"]))
        assert result == ["action_agent"]

    def test_route_to_both(self) -> None:
        fake_settings = FakeSettings()
        graph = WorkflowGraph(
            supervisor_agent=SupervisorAgent(settings=fake_settings),  # type: ignore[arg-type]
            policy_agent=FakePolicyRetriever(),  # type: ignore[arg-type]
            action_agent=FakeActionAgent(),  # type: ignore[arg-type]
        )
        result = graph._route_after_supervisor(self._make_state(["policy_agent", "action_agent"]))
        assert result == ["policy_agent", "action_agent"]

    def test_default_to_both_when_empty(self) -> None:
        fake_settings = FakeSettings()
        graph = WorkflowGraph(
            supervisor_agent=SupervisorAgent(settings=fake_settings),  # type: ignore[arg-type]
            policy_agent=FakePolicyRetriever(),  # type: ignore[arg-type]
            action_agent=FakeActionAgent(),  # type: ignore[arg-type]
        )
        result = graph._route_after_supervisor(self._make_state([]))
        assert result == ["policy_agent", "action_agent"]


# =========================================================================
# 8. Supervisor Prompt Quality — sanity check
# =========================================================================


class TestSupervisorPrompt:
    """The prompt itself should contain key routing instructions."""

    def test_prompt_mentions_both_agents(self) -> None:
        assert "policy_agent" in SUPERVISOR_SYSTEM_PROMPT
        assert "action_agent" in SUPERVISOR_SYSTEM_PROMPT

    def test_prompt_has_examples(self) -> None:
        assert "Examples" in SUPERVISOR_SYSTEM_PROMPT or "example" in SUPERVISOR_SYSTEM_PROMPT

    def test_prompt_has_routing_rules(self) -> None:
        assert "NEVER" in SUPERVISOR_SYSTEM_PROMPT or "Routing Rules" in SUPERVISOR_SYSTEM_PROMPT


# =========================================================================
# 9. Full Graph Integration — Deterministic Only
# =========================================================================


class TestFullGraphDeterministicRouting:
    """End-to-end test: invoke the compiled graph with a deterministic query
    and assert the correct agents execute."""

    def _build_graph(self) -> tuple[WorkflowGraph, FakeActionAgent]:
        fake_settings = FakeSettings()
        fake_action = FakeActionAgent()
        graph = WorkflowGraph(
            supervisor_agent=SupervisorAgent(settings=fake_settings),  # type: ignore[arg-type]
            policy_agent=FakePolicyRetriever(),  # type: ignore[arg-type]
            action_agent=fake_action,  # type: ignore[arg-type]
        )
        return graph, fake_action

    def test_action_query_does_not_call_policy_agent(self) -> None:
        graph, fake_action = self._build_graph()
        state = graph.compiled.invoke(
            {
                "user_input": "What is my sick leave balance? My ID is EMP-999",
                "messages": [],
                "executed_agents": [],
            },
            config={"configurable": {"thread_id": "test-integration-1"}},
        )
        executed = state.get("executed_agents", [])
        assert "action_agent" in executed, "action_agent should have run"
        assert "policy_agent" not in executed, (
            f"policy_agent should NOT have run for action-only query. "
            f"Got agents: {executed}"
        )

    def test_policy_query_does_not_call_action_agent(self) -> None:
        graph, _ = self._build_graph()
        state = graph.compiled.invoke(
            {
                "user_input": "What is the notice period policy?",
                "messages": [],
                "executed_agents": [],
            },
            config={"configurable": {"thread_id": "test-integration-2"}},
        )
        executed = state.get("executed_agents", [])
        assert "policy_agent" in executed, "policy_agent should have run"
        assert "action_agent" not in executed, (
            f"action_agent should NOT have run for policy-only query. "
            f"Got agents: {executed}"
        )

    def test_action_result_is_not_unsupported_for_policy_query(self) -> None:
        """Pure policy queries must never produce an action_result with
        status 'unsupported' — action_agent should not even run."""
        graph, _ = self._build_graph()
        state = graph.compiled.invoke(
            {
                "user_input": "What is the notice period policy?",
                "messages": [],
                "executed_agents": [],
            },
            config={"configurable": {"thread_id": "test-integration-3"}},
        )
        executed = state.get("executed_agents", [])
        action_result = state.get("action_result")
        assert "action_agent" not in executed, (
            "action_agent ran for a pure policy query! "
            "The execution trace should never show ActionAgent failures for pure policy queries."
        )
        assert action_result is None, (
            f"Expected no action_result for policy-only query, got: {action_result}"
        )
