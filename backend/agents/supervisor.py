"""Supervisor agent implementation."""

from dataclasses import dataclass
from typing import Literal, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from backend.config.settings import Settings


class SupervisorDecision(BaseModel):
    """Structured routing decision produced by the supervisor."""

    next_agents: list[Literal["policy_agent", "action_agent"]] = Field(
        description="The downstream agents that should run for this request.",
        min_length=1,
    )
    rationale: str = Field(
        description="Short explanation describing why the selected agents are needed.",
    )


SUPERVISOR_SYSTEM_PROMPT = """
You are the supervisor for an HR workflow engine.

Decide which specialized agents should handle the user request:
- policy_agent: use for policy interpretation, compliance, approvals,
  eligibility checks, or rule validation.
- action_agent: use for workflow execution, task completion, record changes,
  notifications, or operational follow-through.

Return structured output only.
Select one or both agents.
""".strip()


@dataclass(slots=True)
class SupervisorAgent:
    """Coordinates workflow execution across specialized agents using structured output."""

    settings: Settings
    name: str = "supervisor_agent"

    def _default_decision(self, rationale: str) -> SupervisorDecision:
        """Return a safe fallback routing decision."""
        return SupervisorDecision(
            next_agents=["policy_agent", "action_agent"],
            rationale=rationale,
        )

    def decide(
        self, user_input: str, messages: list[BaseMessage] | None = None
    ) -> SupervisorDecision:
        """Return a structured routing decision for the workflow."""
        if not self.settings.openai_api_key:
            return self._default_decision(
                rationale=(
                    "OpenAI API key is not configured, so the workflow defaults " "to both agents."
                ),
            )

        router = ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
            temperature=0,
        ).with_structured_output(SupervisorDecision)

        try:
            chat_messages: list[BaseMessage] = [SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT)]
            if messages:
                for msg in messages:
                    if isinstance(msg, (HumanMessage, AIMessage)):
                        chat_messages.append(msg)
            chat_messages.append(HumanMessage(content=user_input))

            decision = router.invoke(chat_messages)
            return cast(SupervisorDecision, decision)
        except Exception:
            return self._default_decision(
                rationale=(
                    "OpenAI was unreachable or misconfigured during routing, so the workflow "
                    "defaults to both agents."
                ),
            )
