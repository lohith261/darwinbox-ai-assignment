"""CLI entrypoint for indexing the HR policy corpus."""

from backend.config.settings import get_settings
from backend.rag.pipeline import PolicyRetrievalPipeline
from backend.tracing.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    """Ingest the markdown policy into ChromaDB."""
    settings = get_settings()
    configure_logging(settings.log_level)
    pipeline = PolicyRetrievalPipeline(settings)
    summary = pipeline.ingest()
    logger.info(
        "indexed_policy_corpus",
        source=summary.source,
        sections_loaded=summary.sections_loaded,
        chunks_indexed=summary.chunks_indexed,
    )


if __name__ == "__main__":
    main()
