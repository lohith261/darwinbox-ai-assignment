"""ChromaDB persistence for policy chunks."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import chromadb
from chromadb.api.models.Collection import Collection

from backend.rag.models import PolicyChunk, RetrievalHit


class PolicyVectorStore:
    """Thin ChromaDB wrapper for policy ingestion and retrieval."""

    def __init__(self, persist_directory: Path, collection_name: str) -> None:
        self._persist_directory = persist_directory
        self._collection_name = collection_name
        self._persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._persist_directory))

    def get_collection(self) -> Collection:
        """Return the policy collection, creating it if needed."""
        return self._client.get_or_create_collection(name=self._collection_name)

    def has_documents(self) -> bool:
        """Return whether the collection currently contains any chunks."""
        return self.get_collection().count() > 0

    def upsert_chunks(self, chunks: list[PolicyChunk], embeddings: list[list[float]]) -> int:
        """Persist embedded chunks into Chroma."""
        collection = self.get_collection()
        vectors = cast(list[Sequence[float] | Sequence[int]], embeddings)
        collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            embeddings=vectors,
            metadatas=[
                {
                    "source": chunk.source,
                    "title": chunk.title,
                    "order": chunk.order,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        )
        return len(chunks)

    def query(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        """Run a similarity search over the policy collection."""
        collection = self.get_collection()
        query_embeddings = cast(list[Sequence[float] | Sequence[int]], [query_embedding])
        result = collection.query(query_embeddings=query_embeddings, n_results=top_k)

        ids = cast(list[list[str]], result["ids"])[0]
        documents = cast(list[list[str]], result["documents"] or [[]])[0]
        metadatas = cast(list[list[Mapping[str, Any]]], result["metadatas"] or [[]])[0]
        distances = cast(list[list[float]], result["distances"] or [[]])[0]

        hits: list[RetrievalHit] = []
        for rank, (chunk_id, document, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances, strict=False),
            start=1,
        ):
            metadata_map = dict(metadata) if isinstance(metadata, dict) else {}
            hits.append(
                RetrievalHit(
                    chunk_id=str(chunk_id),
                    source=str(metadata_map.get("source", "")),
                    title=str(metadata_map.get("title", "Unknown Section")),
                    content=str(document),
                    rank=rank,
                    distance=float(distance) if distance is not None else None,
                )
            )
        return hits

    def peek(self, limit: int = 5) -> dict[str, Any]:
        """Return a small sample of collection contents for diagnostics."""
        return cast(dict[str, Any], self.get_collection().peek(limit=limit))
