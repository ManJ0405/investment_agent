"""Retrieval helper for RAG queries against pgvector chunks."""

from __future__ import annotations

from .embeddings import EmbeddingClient
from .repository import RagRepository


def retrieve_context(
    query: str,
    ticker: str | None = None,
    form_types: list[str] | None = None,
    top_k: int = 6,
) -> list[dict]:
    repo = RagRepository()
    embedder = EmbeddingClient()
    qvec = embedder.embed_text(query)
    rows = repo.similarity_search(
        query_vector=qvec,
        ticker=ticker,
        form_types=form_types,
        k=top_k,
    )
    return [
        {
            "ticker": row.ticker,
            "form_type": row.form_type,
            "filing_date": row.filing_date,
            "section_name": row.section_name,
            "chunk_text": row.chunk_text,
            "distance": row.score,
        }
        for row in rows
    ]

