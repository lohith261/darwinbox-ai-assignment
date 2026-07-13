"""Policy agent implementation backed by retrieved policy context."""

from dataclasses import dataclass
from typing import Any, Protocol

from langchain_core.messages import AIMessage

from backend.rag.models import RetrievalHit


class PolicyRetriever(Protocol):
    """Protocol for retrieval pipelines used by the policy agent."""

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        """Retrieve policy chunks relevant to a user query."""


@dataclass(slots=True)
class PolicyAgent:
    """Answers policy questions using retrieved policy context only."""

    retriever: PolicyRetriever
    name: str = "policy_agent"

    def run(self, state: Any) -> dict[str, object]:
        """Return a retrieval-grounded policy answer or an unavailable notice."""
        user_input = state.get("user_input", "") if isinstance(state, dict) else str(state)

        hits = self.retriever.retrieve(user_input, top_k=4)

        if not hits:
            content = (
                "Policy unavailable: I could not find a supported answer in the "
                "retrieved HR policy context."
            )
            return {
                "messages": [AIMessage(content=content, name=self.name)],
                "executed_agents": [self.name],
                "policy_result": {
                    "status": "unavailable",
                    "answer": content,
                    "citations": [],
                },
            }

        content = self._compose_answer(hits)
        return {
            "messages": [AIMessage(content=content, name=self.name)],
            "executed_agents": [self.name],
            "policy_result": {
                "status": "grounded",
                "answer": content,
                "citations": [
                    {
                        "title": hit.title,
                        "source": hit.source,
                        "rank": hit.rank,
                    }
                    for hit in hits
                ],
            },
        }

    def _compose_answer(self, hits: list[RetrievalHit]) -> str:
        """Compose an answer exclusively from retrieved policy chunks."""
        lines = ["Based on the retrieved HR policy context:"]
        for hit in hits[:3]:
            lines.append(f"- {hit.title}: {hit.content}")
        return "\n".join(lines)
