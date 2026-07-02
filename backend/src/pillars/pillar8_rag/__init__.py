"""Pillar 8 RAG package for SEC 10-K / 10-Q ingestion and retrieval."""

from .ingest import ingest_filings_for_ticker
from .retrieve import retrieve_context

__all__ = ["ingest_filings_for_ticker", "retrieve_context"]

