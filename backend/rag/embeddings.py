"""Embedding utilities for policy retrieval."""

from typing import cast

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from backend.config.settings import Settings


class DummyEmbeddings(Embeddings):
    """Mock embeddings client returning zero vectors for offline/dummy keys."""

    def __init__(self, size: int = 1536) -> None:
        self.size = size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return zero embeddings for all documents."""
        return [[0.0] * self.size for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return zero embedding for query."""
        return [0.0] * self.size


def _is_dummy_key(key: str) -> bool:
    """Check if the configured API key represents a placeholder or mock value."""
    cleaned = key.strip().lower()
    return not cleaned or "mock" in cleaned or "xxxx" in cleaned or "your_openai_api_key" in cleaned


def build_embeddings(settings: Settings) -> Embeddings:
    """Create the embedding client used for ingestion and retrieval."""
    if _is_dummy_key(settings.openai_api_key):
        return DummyEmbeddings()

    kwargs = {
        "model": settings.openai_embedding_model,
        "api_key": SecretStr(settings.openai_api_key),
    }
    return cast(Embeddings, OpenAIEmbeddings(**kwargs))
