"""CLI entrypoint for indexing the HR policy corpus."""

from backend.config.settings import get_settings
from backend.rag.pipeline import PolicyRetrievalPipeline


def main() -> None:
    """Ingest the markdown policy into ChromaDB."""
    settings = get_settings()
    pipeline = PolicyRetrievalPipeline(settings)
    summary = pipeline.ingest()
    print(
        "Indexed policy corpus",
        {
            "source": summary.source,
            "sections_loaded": summary.sections_loaded,
            "chunks_indexed": summary.chunks_indexed,
        },
    )


if __name__ == "__main__":
    main()
