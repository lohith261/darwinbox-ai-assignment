"""End-to-end retrieval pipeline for HR policy search."""

from dataclasses import dataclass
from pathlib import Path

from openai import APIConnectionError, APIError, APITimeoutError

from backend.config.settings import Settings
from backend.rag.chunking import chunk_policy_sections
from backend.rag.embeddings import build_embeddings
from backend.rag.loader import load_policy_markdown
from backend.rag.models import RetrievalHit
from backend.rag.vectorstore import PolicyVectorStore
from backend.tracing.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class IngestionSummary:
    """A small summary of policy ingestion results."""

    sections_loaded: int
    chunks_indexed: int
    source: str


class PolicyRetrievalPipeline:
    """Load, index, and query the HR policy corpus."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._vectorstore = PolicyVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )
        self._embeddings_client = build_embeddings(settings)

    def ingest(self, document_path: Path | None = None) -> IngestionSummary:
        """Load the markdown policy and index it in Chroma."""
        resolved_path = document_path or self._settings.policy_document_path
        sections = load_policy_markdown(resolved_path)
        chunks = chunk_policy_sections(
            sections=sections,
            chunk_size=self._settings.policy_chunk_size,
            chunk_overlap=self._settings.policy_chunk_overlap,
        )

        vectors = self._embeddings_client.embed_documents([chunk.content for chunk in chunks])
        indexed = self._vectorstore.upsert_chunks(chunks, vectors)

        logger.info(
            "policy_ingestion_completed",
            sections_loaded=len(sections),
            chunks_indexed=indexed,
            source=str(resolved_path),
        )

        return IngestionSummary(
            sections_loaded=len(sections),
            chunks_indexed=indexed,
            source=str(resolved_path),
        )

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalHit]:
        """Retrieve policy chunks relevant to a query with distance filters."""
        if not self._settings.openai_api_key:
            logger.warning("policy_retrieval_failed", reason="missing_openai_key")
            return []

        if not self._vectorstore.has_documents():
            logger.warning("policy_retrieval_failed", reason="vectorstore_empty")
            return []

        try:
            query_embedding = self._embeddings_client.embed_query(query)
        except (APIConnectionError, APIError, APITimeoutError) as e:
            logger.error("policy_retrieval_failed", error=str(e))
            return []

        all_hits = self._vectorstore.query(query_embedding=query_embedding, top_k=top_k)

        # Enforce distance threshold to prevent low-similarity hallucinations (threshold = 1.0)
        filtered_hits: list[RetrievalHit] = []
        for hit in all_hits:
            if hit.distance is None or hit.distance <= 1.0:
                filtered_hits.append(hit)
            else:
                logger.info(
                    "policy_retrieval_filtered_out",
                    chunk_id=hit.chunk_id,
                    title=hit.title,
                    distance=hit.distance,
                )

        logger.info(
            "policy_retrieval_completed",
            query=query,
            top_k=top_k,
            hits_count=len(filtered_hits),
            original_count=len(all_hits),
        )
        return filtered_hits
