"""Smoke tests for the application scaffold."""

from fastapi.testclient import TestClient

from backend.main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-Ms" in response.headers
