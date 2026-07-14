"""LangGraph workflow assembly for the HR engine with execution tracing and optimized routing."""

import operator
import time
import uuid
from datetime import datetime
from typing import Annotated, Any, NotRequired, TypedDict, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from backend.agents.action import ActionAgent
from backend.agents.policy import PolicyAgent
from backend.agents.supervisor import SUPERVISOR_SYSTEM_PROMPT, SupervisorAgent, SupervisorDecision


def merge_trace_data(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    """Reducer to merge trace updates from parallel agent execution steps."""
    if not left:
        return right or {}
    if not right:
        return left

    left_agents = list(left.get("agents", []))
    right_agents = list(right.get("agents", []))

    # Append agents that aren't already present (to avoid duplicates)
    seen_agent_names = {a.get("agent_name") for a in left_agents}
    combined_agents = list(left_agents)
    for a in right_agents:
        if a.get("agent_name") not in seen_agent_names:
            combined_agents.append(a)
            seen_agent_names.add(a.get("agent_name"))

    # Recalculate totals from combined list of agents
    total_latency = sum(a.get("latency_sec", 0.0) for a in combined_agents)
    total_cost = sum(a.get("cost", 0.0) for a in combined_agents)

    return {
        "trace_id": left.get("trace_id") or right.get("trace_id"),
        "session_id": left.get("session_id") or right.get("session_id"),
        "timestamp": left.get("timestamp") or right.get("timestamp"),
        "user_input": left.get("user_input") or right.get("user_input"),
        "agents": combined_agents,
        "total_latency_sec": total_latency,
        "total_cost": total_cost,
        "naive_cost": left.get("naive_cost", 0.0) or right.get("naive_cost", 0.0),
        "status": right.get("status") or left.get("status"),
    }


class WorkflowState(TypedDict):
    """Graph state for the HR workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    route_decision: NotRequired[dict[str, Any]]
    executed_agents: Annotated[list[str], operator.add]
    policy_result: NotRequired[dict[str, Any]]
    action_result: NotRequired[dict[str, Any]]
    employee_id: NotRequired[str]
    start_date: NotRequired[str]
    end_date: NotRequired[str]
    trace_id: NotRequired[str]
    trace_data: Annotated[dict[str, Any], merge_trace_data]


class WorkflowGraph:
    """Encapsulates the LangGraph workflow and its checkpointer."""

    def __init__(
        self,
        supervisor_agent: SupervisorAgent,
        policy_agent: PolicyAgent,
        action_agent: ActionAgent,
    ) -> None:
        self._supervisor_agent = supervisor_agent
        self._policy_agent = policy_agent
        self._action_agent = action_agent
        self._checkpointer = InMemorySaver()
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        workflow = StateGraph(WorkflowState)

        workflow.add_node("supervisor_agent", self._run_supervisor)
        workflow.add_node("policy_agent", self._run_policy_agent)
        workflow.add_node("action_agent", self._run_action_agent)

        workflow.add_edge(START, "supervisor_agent")
        workflow.add_conditional_edges(
            "supervisor_agent",
            self._route_after_supervisor,
            ["policy_agent", "action_agent"],
        )
        workflow.add_edge("policy_agent", END)
        workflow.add_edge("action_agent", END)

        return workflow.compile(checkpointer=self._checkpointer)

    @staticmethod
    def _has_action_word_pair(q_words: set[str], verbs: set[str], noun: str) -> bool:
        """Check whether any *verb* from *verbs* and *noun* both appear in *q_words*.
        This catches non-contiguous patterns like "apply for 2 days casual leave".
        """
        return noun in q_words and bool(q_words & verbs)

    def _is_deterministic(self, query: str) -> tuple[bool, list[str], str]:
        """
        Classify a query deterministically by pattern matching.

        Returns:
            (True, ["action_agent"], rationale) for action-only queries
            (True, ["policy_agent"], rationale) for policy-only queries
            (False, [], "") when the query is ambiguous or mixed — falls through to LLM

        Strict ordering:
          1. Check action patterns first (they are more transactional and urgent).
             BEFORE returning action, verify the query does NOT contain strong policy
             signals — if it does, defer to the LLM for disambiguation.
          2. Check policy patterns *only if* the query is unambiguously policy-focused
             and contains NO action keywords.
          3. Mixed queries (action + policy keywords together) are routed to the LLM.
        """
        q = query.lower()
        q_words = set(q.split())

        # ---- Strong policy signals that override action matching ----
        # When the query matches an action pattern BUT also contains any of these
        # policy phrases, the query is ambiguous — defer to the LLM.
        _STRONG_POLICY = [
            "policy",
            "what is the policy",
            "what does the policy say",
            "notice period",
            "work from home",
            "remote work",
        ]

        # ---- 1. Action-only patterns (transactional / data operations) ----
        # Each entry: (list_of_substring_keys, list_of_word_set_checks, rationale)
        # The pattern matches if ANY substring key is found, OR if the word-check
        # function returns True.
        _ACTION_PATTERNS: list[tuple[list[str], str]] = [
            (["leave balance", "remaining leave", "check balance", "how many days of leave"],
             "Bypassed LLM: Query matched leave balance pattern."),
            (["payslip", "salary", "download payslip", "pay slip"],
             "Bypassed LLM: Query matched payslip pattern."),
            (["apply leave", "request leave", "take leave", "apply for leave",
              "applying for leave", "requesting leave", "taking leave"],
             "Bypassed LLM: Query matched leave application pattern."),
        ]

        # Word-set based matching for patterns that users naturally type with
        # modifiers between the verb and noun (e.g. "apply for 2 days casual leave").
        _ACTION_WORD_PAIRS: list[tuple[set[str], str, str]] = [
            ({"apply", "applying", "applies", "request", "requesting", "requests",
              "take", "taking", "takes"},
             "leave",
             "Bypassed LLM: Query matched leave application pattern."),
        ]

        def _matches_action() -> bool:
            for keywords, _ in _ACTION_PATTERNS:
                if any(k in q for k in keywords):
                    return True
            for verbs, noun, _ in _ACTION_WORD_PAIRS:
                if self._has_action_word_pair(q_words, verbs, noun):
                    return True
            return False

        if _matches_action():
            # If the query also has strong policy signals, it's ambiguous
            # (e.g. "What is the leave balance policy?") → defer to LLM
            if any(k in q for k in _STRONG_POLICY):
                return False, [], ""
            return True, ["action_agent"], "Bypassed LLM: Query matched action pattern."

        # ---- 2. Policy-only patterns (knowledge / rule lookups) ----
        _POLICY_KEYWORDS = [
            "policy",
            "notice period",
            "work from home",
            "remote work",
            "attendance policy",
            "leave policy",
            "payroll policy",
            "maternity leave policy",
            "paternity leave policy",
            "what is the policy on",
            "what does the policy say",
            "sick leave policy",
            "casual leave policy",
            "earned leave policy",
        ]
        _ACTION_TRIGGERS = {
            "balance", "apply", "applying", "applies",
            "payslip", "salary",
            "remaining",
        }

        is_policy_candidate = any(k in q for k in _POLICY_KEYWORDS)
        has_action_overlap = bool(q_words & _ACTION_TRIGGERS)

        if is_policy_candidate and not has_action_overlap:
            return True, ["policy_agent"], "Bypassed LLM: Query matched policy pattern."

        # ---- 3. Ambiguous / mixed — defer to LLM supervisor ----
        return False, [], ""

    def _run_supervisor(self, state: WorkflowState, config: RunnableConfig) -> dict[str, object]:
        start_time = time.perf_counter()

        # Estimate naive tokens (what we would use if we always routed via LLM)
        prompt_str = SUPERVISOR_SYSTEM_PROMPT + state["user_input"]
        naive_prompt_tokens = len(prompt_str) // 4
        naive_completion_tokens = 60
        naive_cost = (naive_prompt_tokens * 0.15 + naive_completion_tokens * 0.60) / 1_000_000

        # Check optimized routing strategy
        is_det, next_agents, rationale = self._is_deterministic(state["user_input"])

        if is_det:
            # Deterministic route: Bypassed LLM
            decision = SupervisorDecision(next_agents=next_agents, rationale=rationale)
            prompt_tokens = 0
            completion_tokens = 0
            cost = 0.0
            latency = time.perf_counter() - start_time
        else:
            # LLM route
            decision = self._supervisor_agent.decide(state["user_input"], state.get("messages", []))
            prompt_tokens = naive_prompt_tokens
            completion_tokens = naive_completion_tokens
            cost = naive_cost
            latency = time.perf_counter() - start_time

        agent_trace = {
            "agent_name": "supervisor_agent",
            "latency_sec": latency,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": cost,
            "failures": [],
            "retrieved_documents": [],
            "tool_calls": [],
        }

        trace_id = state.get("trace_id") or str(uuid.uuid4())
        session_id = config.get("configurable", {}).get("thread_id", "unknown")

        prev_trace_data = state.get("trace_data") or {}
        agents_list = list(prev_trace_data.get("agents", []))
        agents_list.append(agent_trace)

        trace_data = {
            "trace_id": trace_id,
            "session_id": session_id,
            "timestamp": prev_trace_data.get("timestamp") or datetime.now().isoformat(),
            "user_input": state["user_input"],
            "agents": agents_list,
            "total_latency_sec": prev_trace_data.get("total_latency_sec", 0.0) + latency,
            "total_cost": prev_trace_data.get("total_cost", 0.0) + cost,
            "naive_cost": prev_trace_data.get("naive_cost", 0.0) + naive_cost,
            "status": "in_progress",
        }

        content = (
            "SupervisorAgent selected: "
            f"{', '.join(decision.next_agents)}. Rationale: {decision.rationale}"
        )
        return {
            "messages": [
                HumanMessage(content=state["user_input"]),
                AIMessage(content=content, name=self._supervisor_agent.name),
            ],
            "route_decision": decision.model_dump(),
            "executed_agents": [self._supervisor_agent.name],
            "trace_id": trace_id,
            "trace_data": trace_data,
        }

    def _route_after_supervisor(self, state: WorkflowState) -> list[str]:
        route_decision = state.get("route_decision", {})
        next_agents = route_decision.get("next_agents", [])
        return cast(list[str], next_agents or ["policy_agent", "action_agent"])

    def _run_policy_agent(self, state: WorkflowState) -> dict[str, object]:
        start_time = time.perf_counter()

        result = self._policy_agent.run(state)

        latency = time.perf_counter() - start_time

        # Captured documents
        retrieved_docs = []
        policy_result = result.get("policy_result", {})
        citations = policy_result.get("citations", []) if isinstance(policy_result, dict) else []
        if citations:
            for cit in citations:
                if isinstance(cit, dict):
                    retrieved_docs.append(
                        {
                            "title": cit.get("title"),
                            "source": cit.get("source"),
                            "rank": cit.get("rank"),
                        }
                    )

        agent_trace = {
            "agent_name": "policy_agent",
            "latency_sec": latency,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost": 0.0,
            "failures": [],
            "retrieved_documents": retrieved_docs,
            "tool_calls": [],
        }

        prev_trace_data = state.get("trace_data") or {}
        agents_list = list(prev_trace_data.get("agents", []))
        agents_list.append(agent_trace)

        trace_data = {
            **prev_trace_data,
            "agents": agents_list,
            "total_latency_sec": prev_trace_data.get("total_latency_sec", 0.0) + latency,
            "status": "in_progress",
        }

        return {
            **result,
            "trace_data": trace_data,
        }

    def _run_action_agent(self, state: WorkflowState) -> dict[str, object]:
        start_time = time.perf_counter()

        result = self._action_agent.run(state)

        latency = time.perf_counter() - start_time

        # Captured tool calls from result["action_result"]
        tool_calls_trace = []
        action_result = result.get("action_result", {})
        if isinstance(action_result, dict):
            tool_name = action_result.get("tool")
            if tool_name:
                tool_output = action_result.get("output", {})
                trace_meta = (
                    tool_output.get("trace_metadata", {}) if isinstance(tool_output, dict) else {}
                )
                if isinstance(tool_output, dict):
                    tool_calls_trace.append(
                        {
                            "tool_name": tool_name,
                            "arguments": {
                                "employee_id": tool_output.get("employee_id"),
                                "leave_type": tool_output.get("leave_type"),
                                "start_date": tool_output.get("start_date"),
                                "end_date": tool_output.get("end_date"),
                                "month": tool_output.get("month"),
                                "year": tool_output.get("year"),
                            },
                            "latency_sec": (
                                trace_meta.get("latency_sec", 0.0)
                                if isinstance(trace_meta, dict)
                                else 0.0
                            ),
                            "retries": (
                                trace_meta.get("retries", 0) if isinstance(trace_meta, dict) else 0
                            ),
                            "failures": (
                                trace_meta.get("failures", [])
                                if isinstance(trace_meta, dict)
                                else []
                            ),
                            "status": tool_output.get("status", "success"),
                        }
                    )

        agent_trace = {
            "agent_name": "action_agent",
            "latency_sec": latency,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost": 0.0,
            "failures": [],
            "retrieved_documents": [],
            "tool_calls": tool_calls_trace,
        }

        prev_trace_data = state.get("trace_data") or {}
        agents_list = list(prev_trace_data.get("agents", []))
        agents_list.append(agent_trace)

        trace_data = {
            **prev_trace_data,
            "agents": agents_list,
            "total_latency_sec": prev_trace_data.get("total_latency_sec", 0.0) + latency,
            "status": "in_progress",
        }

        return {
            **result,
            "trace_data": trace_data,
        }

    @property
    def compiled(self) -> Any:
        """Expose the compiled graph."""
        return self._graph

    def mermaid_diagram(self) -> str:
        """Return a Mermaid representation of the graph."""
        try:
            graph = self._graph.get_graph(xray=True)
        except TypeError:
            graph = self._graph.get_graph()
        draw_mermaid = getattr(graph, "draw_mermaid", None)
        if callable(draw_mermaid):
            return str(draw_mermaid())

        return "\n".join(
            [
                "graph TD",
                "    START --> supervisor_agent",
                "    supervisor_agent --> policy_agent",
                "    supervisor_agent --> action_agent",
                "    policy_agent --> END",
                "    action_agent --> END",
            ]
        )
