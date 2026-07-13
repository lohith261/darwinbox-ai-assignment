"""Shared models for the policy retrieval pipeline."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PolicySection:
    """A logical section parsed from the policy markdown file."""

    source: Path
    title: str
    content: str
    order: int


@dataclass(slots=True)
class PolicyChunk:
    """A chunked portion of a policy section ready for embeddings."""

    chunk_id: str
    source: str
    title: str
    content: str
    order: int
    chunk_index: int


@dataclass(slots=True)
class RetrievalHit:
    """A retrieved policy chunk with rank and score metadata."""

    chunk_id: str
    source: str
    title: str
    content: str
    rank: int
    distance: float | None = None
