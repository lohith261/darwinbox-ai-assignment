"""Policy agent tests."""

from typing import Any, cast

from backend.agents.policy import PolicyAgent
from backend.rag.models import RetrievalHit


class EmptyRetriever:
    """Retriever stub returning no results."""

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        return []


class FixedRetriever:
    """Retriever stub returning fixed policy hits."""

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        return [
            RetrievalHit(
                chunk_id="1",
                source="docs/hr_policy.md",
                title="Sick Leave",
                content=(
                    "Full-time employees are eligible for 12 days of Sick Leave "
                    "per calendar year."
                ),
                rank=1,
                distance=0.12,
            )
        ]


def test_policy_agent_returns_unavailable_when_no_context_exists() -> None:
    agent = PolicyAgent(retriever=EmptyRetriever())

    result = cast(dict[str, Any], agent.run("How many sick leave days are available?"))
    policy_result = cast(dict[str, Any], result["policy_result"])

    assert policy_result["status"] == "unavailable"
    assert "Policy unavailable" in policy_result["answer"]


def test_policy_agent_answers_from_retrieved_context_only() -> None:
    agent = PolicyAgent(retriever=FixedRetriever())

    result = cast(dict[str, Any], agent.run("How many sick leave days are available?"))
    policy_result = cast(dict[str, Any], result["policy_result"])

    assert policy_result["status"] == "grounded"
    assert "12 days of Sick Leave" in policy_result["answer"]
