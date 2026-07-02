# Pillar 8 RAG (10-K / 10-Q)

This module ingests SEC filings into Postgres + pgvector and supports retrieval for agent RAG.

## Data Flow

1. Load ticker -> CIK mapping from `https://www.sec.gov/files/company_tickers.json`
2. Fetch company submissions from `https://www.sec.gov/submissions/CIK{cik}.json`
3. Keep only forms `10-K` and `10-Q`
4. Download filing document from SEC archives
5. Parse + chunk text by item sections and sliding windows
6. Embed chunks (`nomic-embed-text` by default)
7. Store metadata + chunks + vectors in Postgres (`rag_companies`, `rag_filings`, `rag_chunks`)
8. Retrieve with vector similarity + optional metadata filters

## SEC Header Requirement

You do not need to register an SEC account for these endpoints.
But SEC requires a descriptive `User-Agent`.

Set in `.env`:

```bash
SEC_API_USER_AGENT="YourName/1.0 (mandes2003@gmail.com)"
```

## Run Ingestion

From `backend/`:

```bash
python scripts/rag_ingest_sec.py --ticker NVDA --ticker AAPL --max-filings 6
```

## Retrieval Example

```python
from pillars.pillar8_rag.retrieve import retrieve_context

chunks = retrieve_context(
    query="What are the key risk factors?",
    ticker="NVDA",
    form_types=["10-K", "10-Q"],
    top_k=6,
)
```

## Scheduler (Server)

Use cron or a workflow scheduler:

- Daily/weekly check for new filings (recommended)
- If you prefer low-frequency update: every 6 months is acceptable for demo

Example cron (every Sunday 02:00):

```cron
0 2 * * 0 cd /app/backend && /usr/bin/python scripts/rag_ingest_sec.py --ticker NVDA --ticker AAPL --max-filings 4
```

