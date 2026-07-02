"""Ingestion pipeline for SEC 10-K / 10-Q into pgvector-backed storage."""

from __future__ import annotations

from .chunking import sliding_chunks, split_sections
from .embeddings import EmbeddingClient
from .repository import RagRepository
from .sec_client import FilingRecord, SecClient


def _build_chunk_payloads(filing: FilingRecord, text: str, embedder: EmbeddingClient) -> list[dict]:
    payloads: list[dict] = []
    chunk_index = 0
    sections = split_sections(text)
    for section_name, section_text in sections:
        for part in sliding_chunks(section_text, chunk_size=1400, overlap=180):
            vec = embedder.embed_text(part)
            payloads.append(
                {
                    "chunk_index": chunk_index,
                    "section_name": section_name,
                    "chunk_text": part,
                    "embedding": vec,
                    "metadata": {
                        "ticker": filing.ticker,
                        "form_type": filing.form_type,
                        "filing_date": filing.filing_date,
                        "accession_no": filing.accession_no,
                    },
                }
            )
            chunk_index += 1
    return payloads


def ingest_filings_for_ticker(
    ticker: str,
    max_filings: int = 8,
    form_types: tuple[str, ...] = ("10-K", "10-Q"),
) -> dict[str, int]:
    sec = SecClient()
    repo = RagRepository()
    embedder = EmbeddingClient()

    repo.init_schema()

    company = sec.get_company_by_ticker(ticker)
    if not company:
        raise ValueError(f"Ticker not found in SEC company list: {ticker}")

    ticker_norm = company["ticker"]
    company_id = repo.upsert_company(
        ticker=ticker_norm,
        company_name=company["company_name"],
        cik=company["cik"],
    )

    filings = sec.get_recent_filings(
        cik=company["cik"],
        ticker=ticker_norm,
        company_name=company["company_name"],
    )
    filings = [f for f in filings if f.form_type in form_types][:max_filings]

    ingested = 0
    for filing in filings:
        text = sec.fetch_filing_text(filing)
        filing_id = repo.upsert_filing(
            company_id=company_id,
            accession_no=filing.accession_no,
            form_type=filing.form_type,
            filing_date=filing.filing_date,
            report_date=filing.report_date,
            filing_url=filing.filing_url,
            content=text,
        )
        chunks = _build_chunk_payloads(filing, text, embedder)
        repo.replace_chunks(filing_id, chunks)
        ingested += 1

    return {"ticker": ticker_norm, "filings_ingested": ingested}

