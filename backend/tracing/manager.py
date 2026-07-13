"""TraceManager abstraction for exporting execution traces."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ToolCallTrace(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    latency_sec: float
    retries: int
    failures: list[str] = Field(default_factory=list)
    status: str


class AgentTrace(BaseModel):
    agent_name: str
    latency_sec: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    cost: float = 0.0


class RequestTrace(BaseModel):
    trace_id: str
    session_id: str
    timestamp: str
    user_input: str
    total_latency_sec: float
    agents: list[AgentTrace] = Field(default_factory=list)
    total_cost: float = 0.0
    status: str


class TraceManager:
    """Manages serialization and persistence of production workflow traces."""

    def __init__(self, export_dir: Path = Path("data/traces")) -> None:
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export(self, trace: RequestTrace) -> Path:
        """Serialize trace model to JSON and save to the traces directory."""
        file_path = self.export_dir / f"trace_{trace.trace_id}.json"
        trace_dict = trace.model_dump()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trace_dict, f, indent=2, default=str)
        return file_path
