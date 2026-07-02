"""Postgres + pgvector repository for RAG metadata and chunks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import psycopg

from db.init_db import make_dsn


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in vector) + "]"


@dataclass
class RetrievedChunk:
    ticker: str
    form_type: str
    filing_date: str
    section_name: str
    chunk_text: str
    score: float


class RagRepository:
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or make_dsn()

    def init_schema(self) -> None:
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rag_companies (
                        id BIGSERIAL PRIMARY KEY,
                        ticker TEXT NOT NULL UNIQUE,
                        company_name TEXT NOT NULL,
                        cik TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rag_filings (
                        id BIGSERIAL PRIMARY KEY,
                        company_id BIGINT NOT NULL REFERENCES rag_companies(id),
                        accession_no TEXT NOT NULL UNIQUE,
                        form_type TEXT NOT NULL,
                        filing_date DATE NOT NULL,
                        report_date DATE NULL,
                        filing_url TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rag_chunks (
                        id BIGSERIAL PRIMARY KEY,
                        filing_id BIGINT NOT NULL REFERENCES rag_filings(id) ON DELETE CASCADE,
                        chunk_index INT NOT NULL,
                        section_name TEXT NOT NULL,
                        chunk_text TEXT NOT NULL,
                        embedding VECTOR(768) NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        UNIQUE(filing_id, chunk_index)
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding
                    ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_rag_filings_company ON rag_filings(company_id, filing_date DESC);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_rag_chunks_filing ON rag_chunks(filing_id);")

    def upsert_company(self, ticker: str, company_name: str, cik: str) -> int:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rag_companies (ticker, company_name, cik)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (ticker)
                    DO UPDATE SET company_name = EXCLUDED.company_name, cik = EXCLUDED.cik, updated_at = NOW()
                    RETURNING id;
                    """,
                    (ticker, company_name, cik),
                )
                company_id = cur.fetchone()[0]
            conn.commit()
        return company_id

    def upsert_filing(
        self,
        company_id: int,
        accession_no: str,
        form_type: str,
        filing_date: str,
        report_date: str | None,
        filing_url: str,
        content: str,
    ) -> int:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rag_filings (
                        company_id, accession_no, form_type, filing_date, report_date, filing_url, content
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (accession_no)
                    DO UPDATE SET
                        filing_url = EXCLUDED.filing_url,
                        content = EXCLUDED.content,
                        updated_at = NOW()
                    RETURNING id;
                    """,
                    (company_id, accession_no, form_type, filing_date, report_date, filing_url, content),
                )
                filing_id = cur.fetchone()[0]
            conn.commit()
        return filing_id

    def replace_chunks(
        self,
        filing_id: int,
        chunks: list[dict[str, Any]],
    ) -> None:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM rag_chunks WHERE filing_id = %s;", (filing_id,))
                for item in chunks:
                    cur.execute(
                        """
                        INSERT INTO rag_chunks (
                            filing_id, chunk_index, section_name, chunk_text, embedding, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb);
                        """,
                        (
                            filing_id,
                            item["chunk_index"],
                            item["section_name"],
                            item["chunk_text"],
                            _vector_literal(item["embedding"]),
                            json.dumps(item.get("metadata", {})),
                        ),
                    )
            conn.commit()

    def similarity_search(
        self,
        query_vector: list[float],
        ticker: str | None = None,
        form_types: list[str] | None = None,
        k: int = 6,
    ) -> list[RetrievedChunk]:
        filters = []
        params: list[Any] = [_vector_literal(query_vector)]

        if ticker:
            filters.append("c.ticker = %s")
            params.append(ticker.upper())
        if form_types:
            filters.append("f.form_type = ANY(%s)")
            params.append(form_types)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        sql = f"""
            SELECT
                c.ticker,
                f.form_type,
                f.filing_date::text,
                rc.section_name,
                rc.chunk_text,
                (rc.embedding <=> %s::vector) AS distance
            FROM rag_chunks rc
            JOIN rag_filings f ON f.id = rc.filing_id
            JOIN rag_companies c ON c.id = f.company_id
            {where_clause}
            ORDER BY rc.embedding <=> %s::vector
            LIMIT %s;
        """
        params.extend([_vector_literal(query_vector), k])

        out: list[RetrievedChunk] = []
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                for row in cur.fetchall():
                    out.append(
                        RetrievedChunk(
                            ticker=row[0],
                            form_type=row[1],
                            filing_date=row[2],
                            section_name=row[3],
                            chunk_text=row[4],
                            score=float(row[5]),
                        )
                    )
        return out

