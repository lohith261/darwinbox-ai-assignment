"""Chunking helpers for policy documents."""

import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.rag.models import PolicyChunk, PolicySection


def chunk_policy_sections(
    sections: list[PolicySection],
    chunk_size: int,
    chunk_overlap: int,
) -> list[PolicyChunk]:
    """Split policy sections into stable chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )

    chunks: list[PolicyChunk] = []
    for section in sections:
        split_texts = splitter.split_text(section.content)
        for chunk_index, split_text in enumerate(split_texts):
            fingerprint = hashlib.sha1(
                f"{section.source}:{section.title}:{chunk_index}:{split_text}".encode()
            ).hexdigest()
            chunks.append(
                PolicyChunk(
                    chunk_id=fingerprint,
                    source=str(section.source),
                    title=section.title,
                    content=split_text,
                    order=section.order,
                    chunk_index=chunk_index,
                )
            )
    return chunks
