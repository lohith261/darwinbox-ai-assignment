"""Unit and integration tests for tracing and production observability."""

import json
import uuid
from pathlib import Path

from backend.agents.action import ActionAgent
from backend.agents.policy import PolicyAgent
from backend.agents.supervisor import SupervisorAgent
from backend.agents.workflow import WorkflowGraph
from backend.config.settings import get_settings
from backend.rag.models import RetrievalHit
from backend.schemas.workflow import WorkflowInvokeRequest
from backend.services.workflow import WorkflowService
from backend.tracing.manager import TraceManager


class MockRetriever:
    """Mock retriever that returns empty hits."""

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        return []


def test_request_generates_json_trace() -> None:
    settings = get_settings()
    settings.openai_api_key = "mock-openai-key"

    supervisor = SupervisorAgent(settings=settings)
    policy = PolicyAgent(retriever=MockRetriever())
    action = ActionAgent()
    workflow_graph = WorkflowGraph(
        supervisor_agent=supervisor, policy_agent=policy, action_agent=action
    )

    # Use a custom export directory for testing
    test_traces_dir = Path("data/test_traces")
    if test_traces_dir.exists():
        for old_file in test_traces_dir.glob("trace_*.json"):
            old_file.unlink()
    trace_manager = TraceManager(export_dir=test_traces_dir)

    service = WorkflowService(workflow_graph=workflow_graph, trace_manager=trace_manager)

    session_id = str(uuid.uuid4())
    req = WorkflowInvokeRequest(
        user_input="Apply sick leave for employee EMP-111 from 2026-08-01 to 2026-08-05",
        session_id=session_id,
    )

    service.invoke(request=req)

    # Clean up and find the generated file
    trace_files = list(test_traces_dir.glob("trace_*.json"))
    assert len(trace_files) >= 1

    generated_trace_file = trace_files[0]

    with open(generated_trace_file, encoding="utf-8") as f:
        trace_data = json.load(f)

    # Assert trace schema structure
    assert trace_data["trace_id"] is not None
    assert trace_data["session_id"] == session_id
    assert trace_data["user_input"] == req.user_input
    assert trace_data["total_latency_sec"] > 0.0
    assert trace_data["total_cost"] >= 0.0
    assert trace_data["status"] == "completed"
    assert "timestamp" in trace_data

    # Assert agent specific metrics are present
    agents = trace_data["agents"]
    assert len(agents) >= 1

    # Check supervisor agent trace metrics
    supervisor_trace = next(a for a in agents if a["agent_name"] == "supervisor_agent")
    assert supervisor_trace["latency_sec"] > 0.0
    assert supervisor_trace["prompt_tokens"] >= 0
    assert supervisor_trace["completion_tokens"] >= 0
    assert supervisor_trace["cost"] >= 0.0

    # Check action agent trace metrics (if executed)
    action_trace = next((a for a in agents if a["agent_name"] == "action_agent"), None)
    if action_trace:
        assert action_trace["latency_sec"] > 0.0
        assert len(action_trace["tool_calls"]) >= 1
        tool_call = action_trace["tool_calls"][0]
        assert tool_call["tool_name"] == "apply_leave"
        assert tool_call["latency_sec"] > 0.0
        assert "failures" in tool_call
        assert "retries" in tool_call
        assert tool_call["status"] is not None

    # Clean up test directory files
    for tf in trace_files:
        tf.unlink()
    test_traces_dir.rmdir()
