"""Supervisor agent implementation."""

from dataclasses import dataclass, field
from typing import Any, Literal, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from backend.config.settings import Settings
from backend.tracing.logging import get_logger

logger = get_logger(__name__)


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
You are the supervisor for an HR workflow engine. Your job is to route user requests
correctly between two specialized agents.

--- Agent Roles ---

**policy_agent**
- Answers questions about HR policies, rules, guidelines, and compliance.
- This agent uses a vector index over the company's HR policy handbook to
  provide grounded, citation-backed answers.
- Use this for queries about: leave policy, notice period, sick leave rules,
  casual leave rules, earned leave rules, work-from-home policy, remote work,
  attendance policy, payroll policy, maternity leave, paternity leave,
  policy eligibility, approvals, and rule validation.
- Examples: "What is the notice period?", "How many sick leave days do I get?",
  "What is the work from home policy?", "Can casual leave be carried forward?"

**action_agent**
- Performs transactional operations and retrieves data from HR systems.
- This agent uses mock HR API tools (check_leave_balance, apply_leave,
  fetch_payslip) with built-in resilience.
- Use this for queries about: leave balance checks, applying for leave,
  fetching payslips, salary details, or any database update.
- Examples: "What is my sick leave balance? My ID is EMP-999",
  "Apply for 2 days of casual leave", "Fetch my July payslip"

--- Routing Rules ---

1. If the query is ONLY about policy questions (asking what the rules are),
   route ONLY to `["policy_agent"]`.

2. If the query is ONLY about transactional actions (checking balance,
   applying leave, fetching payslip), route ONLY to `["action_agent"]`.

3. If the query is a MIX of policy questions AND action requests
   (e.g. "What is the leave policy and also apply for 2 days"),
   route to BOTH: `["policy_agent", "action_agent"]`.

4. NEVER route a pure policy question to action_agent.

5. NEVER route a pure action request to policy_agent.

Return structured output only. Select one or both agents.
""".strip()


@dataclass(slots=True)
class SupervisorAgent:
    """Coordinates workflow execution across specialized agents using structured output."""

    settings: Settings
    name: str = "supervisor_agent"
    _router: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize the reusable OpenAI Chat model router to avoid reconstruction overhead."""
        if self.settings.openai_api_key:
            kwargs: dict[str, object] = {
                "model": self.settings.openai_model,
                "api_key": self.settings.openai_api_key,
                "temperature": 0,
            }
            if self.settings.openai_base_url:
                kwargs["base_url"] = self.settings.openai_base_url
            self._router = ChatOpenAI(**kwargs).with_structured_output(SupervisorDecision)

    def _default_decision(self, rationale: str) -> SupervisorDecision:
        """Return a safe fallback routing decision."""
        logger.warning("agent_routing_fallback_triggered", rationale=rationale)
        return SupervisorDecision(
            next_agents=["policy_agent", "action_agent"],
            rationale=rationale,
        )

    def decide(
        self, user_input: str, messages: list[BaseMessage] | None = None
    ) -> SupervisorDecision:
        """Return a structured routing decision for the workflow."""
        if self._router is None:
            return self._default_decision(
                rationale=(
                    "OpenAI API key is not configured or router failed initialization, "
                    "so the workflow defaults to both agents."
                ),
            )

        try:
            chat_messages: list[BaseMessage] = [SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT)]
            if messages:
                for msg in messages:
                    if isinstance(msg, (HumanMessage, AIMessage)):
                        chat_messages.append(msg)
            chat_messages.append(HumanMessage(content=user_input))

            decision = self._router.invoke(chat_messages)
            resolved_decision = cast(SupervisorDecision, decision)
            logger.info(
                "agent_routing_completed",
                user_input=user_input,
                next_agents=resolved_decision.next_agents,
                rationale=resolved_decision.rationale,
            )
            return resolved_decision
        except Exception as e:
            return self._default_decision(
                rationale=(
                    f"OpenAI decision routing failed with exception: {e}, "
                    "defaulting to both agents."
                ),
            )
