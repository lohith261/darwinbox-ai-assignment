"""Application state container."""

from dataclasses import dataclass, field

from backend.agents.action import ActionAgent
from backend.agents.policy import PolicyAgent
from backend.agents.supervisor import SupervisorAgent
from backend.agents.workflow import WorkflowGraph
from backend.config.settings import Settings
from backend.rag.pipeline import PolicyRetrievalPipeline
from backend.services.application import ApplicationService
from backend.services.workflow import WorkflowService


@dataclass(slots=True)
class ApplicationContainer:
    """Lightweight dependency container for shared application services."""

    settings: Settings
    supervisor_agent: SupervisorAgent = field(init=False)
    policy_retrieval_pipeline: PolicyRetrievalPipeline = field(init=False)
    policy_agent: PolicyAgent = field(init=False)
    action_agent: ActionAgent = field(default_factory=ActionAgent)
    application_service: ApplicationService = field(init=False)
    workflow_service: WorkflowService = field(init=False)

    def __post_init__(self) -> None:
        """Create shared services once for the application lifetime."""
        self.supervisor_agent = SupervisorAgent(settings=self.settings)
        self.policy_retrieval_pipeline = PolicyRetrievalPipeline(settings=self.settings)
        self.policy_agent = PolicyAgent(retriever=self.policy_retrieval_pipeline)
        self.application_service = ApplicationService(settings=self.settings)
        workflow_graph = WorkflowGraph(
            supervisor_agent=self.supervisor_agent,
            policy_agent=self.policy_agent,
            action_agent=self.action_agent,
        )
        self.workflow_service = WorkflowService(workflow_graph=workflow_graph)
