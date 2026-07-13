"""Workflow API smoke tests."""

from fastapi.testclient import TestClient

from backend.main import app


def test_workflow_invoke_persists_session_state() -> None:
    client = TestClient(app)

    invoke_response = client.post(
        "/api/v1/workflows/invoke",
        json={"user_input": "Please review leave eligibility and trigger the next workflow step."},
    )

    assert invoke_response.status_code == 200
    invoke_payload = invoke_response.json()
    assert invoke_payload["session_id"]
    assert invoke_payload["route_decision"]["next_agents"]
    assert "supervisor_agent" in invoke_payload["graph_visualization"]

    session_response = client.get(f"/api/v1/workflows/sessions/{invoke_payload['session_id']}")

    assert session_response.status_code == 200
    session_payload = session_response.json()
    assert session_payload["session_id"] == invoke_payload["session_id"]
    assert session_payload["messages"]


def test_workflow_graph_visualization_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/workflows/graph")

    assert response.status_code == 200
    assert "mermaid" in response.json()
