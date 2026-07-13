"""Workflow service backed by LangGraph with execution tracing and optimized routing."""

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import BaseMessage

from backend.agents.workflow import WorkflowGraph
from backend.schemas.workflow import (
    GraphVisualizationResponse,
    WorkflowInvokeRequest,
    WorkflowInvokeResponse,
    WorkflowSessionResponse,
)
from backend.tracing.manager import AgentTrace, RequestTrace, ToolCallTrace, TraceManager

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkflowService:
    """Application service for executing the LangGraph workflow."""

    workflow_graph: WorkflowGraph
    trace_manager: TraceManager = field(default_factory=TraceManager)

    def invoke(self, request: WorkflowInvokeRequest) -> WorkflowInvokeResponse:
        """Invoke the workflow with session persistence, route optimization, and trace exporting."""
        session_id = request.session_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        state = self.workflow_graph.compiled.invoke(
            {
                "user_input": request.user_input,
                "messages": [],
                "executed_agents": [],
            },
            config=config,
        )

        naive_cost = 0.0
        optimized_cost = 0.0
        percentage_reduction = 0.0
        latency_sec = 0.0
        prompt_tokens = 0
        completion_tokens = 0

        # Finalize and export trace
        trace_data = state.get("trace_data")
        if isinstance(trace_data, dict):
            trace_data["status"] = "completed"

            naive_cost = trace_data.get("naive_cost", 0.0)
            optimized_cost = trace_data.get("total_cost", 0.0)
            latency_sec = trace_data.get("total_latency_sec", 0.0)

            for a in trace_data.get("agents", []):
                if isinstance(a, dict):
                    prompt_tokens += a.get("prompt_tokens", 0)
                    completion_tokens += a.get("completion_tokens", 0)

            if naive_cost > 0:
                percentage_reduction = ((naive_cost - optimized_cost) / naive_cost) * 100

            try:
                agents_models = []
                for agent_dict in trace_data.get("agents", []):
                    if isinstance(agent_dict, dict):
                        tool_calls_models = []
                        for tc in agent_dict.get("tool_calls", []):
                            if isinstance(tc, dict):
                                tool_calls_models.append(ToolCallTrace(**tc))
                        agent_dict["tool_calls"] = tool_calls_models
                        agents_models.append(AgentTrace(**agent_dict))

                trace_data["agents"] = agents_models
                trace_model = RequestTrace(**trace_data)

                # Export trace
                self.trace_manager.export(trace_model)
                logger.info(f"Exported trace JSON to data/traces/trace_{trace_model.trace_id}.json")
            except Exception as e:
                logger.error(f"Failed to export request trace: {e}")

        return WorkflowInvokeResponse(
            session_id=session_id,
            route_decision=state.get("route_decision", {}),
            executed_agents=state.get("executed_agents", []),
            messages=self._serialize_messages(state.get("messages", [])),
            graph_visualization=self.workflow_graph.mermaid_diagram(),
            policy_result=state.get("policy_result"),
            action_result=state.get("action_result"),
            employee_id=state.get("employee_id"),
            start_date=state.get("start_date"),
            end_date=state.get("end_date"),
            naive_cost=naive_cost,
            optimized_cost=optimized_cost,
            percentage_reduction=percentage_reduction,
            latency_sec=latency_sec,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def get_session(self, session_id: str) -> WorkflowSessionResponse:
        """Return the current checkpointed session state."""
        config = {"configurable": {"thread_id": session_id}}
        snapshot = self.workflow_graph.compiled.get_state(config)
        values = snapshot.values if snapshot else {}

        return WorkflowSessionResponse(
            session_id=session_id,
            next_nodes=list(snapshot.next) if snapshot else [],
            executed_agents=values.get("executed_agents", []),
            route_decision=values.get("route_decision"),
            messages=self._serialize_messages(values.get("messages", [])),
            employee_id=values.get("employee_id"),
            start_date=values.get("start_date"),
            end_date=values.get("end_date"),
        )

    def graph_visualization(self) -> GraphVisualizationResponse:
        """Return the graph visualization."""
        return GraphVisualizationResponse(
            mermaid=self.workflow_graph.mermaid_diagram(),
        )

    @staticmethod
    def _serialize_messages(messages: list[BaseMessage]) -> list[dict[str, Any]]:
        """Convert LangChain messages into API-friendly dictionaries."""
        serialized_messages: list[dict[str, Any]] = []
        for message in messages:
            serialized_messages.append(
                {
                    "type": message.type,
                    "content": message.content,
                    "name": getattr(message, "name", None),
                }
            )
        return serialized_messages
