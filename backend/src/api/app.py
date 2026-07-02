"""FastAPI app exposing production-style endpoints."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from src.pillars.pillar2_trend import Pillar2Input, Pillar2Output, trend_signal
    from src.pillars.pillar8_rag import ingest_filings_for_ticker, retrieve_context
except ModuleNotFoundError:
    from pillars.pillar2_trend import Pillar2Input, Pillar2Output, trend_signal
    from pillars.pillar8_rag import ingest_filings_for_ticker, retrieve_context

app = FastAPI(
    title="Investment Agent API",
    version="0.2.0",
    description="Production-style API for investment agent pillars.",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/pillars/pillar2/trend-signal", response_model=Pillar2Output)
def pillar2_trend_signal(payload: Pillar2Input) -> Pillar2Output:
    return trend_signal(payload)


class RagRetrieveRequest(BaseModel):
    query: str = Field(min_length=3)
    ticker: str | None = None
    form_types: list[str] | None = None
    top_k: int = Field(default=6, ge=1, le=20)


@app.post("/api/v1/rag/ingest/{ticker}")
def rag_ingest_ticker(ticker: str, max_filings: int = 8) -> dict:
    return ingest_filings_for_ticker(ticker=ticker, max_filings=max_filings)


@app.post("/api/v1/rag/retrieve")
def rag_retrieve(payload: RagRetrieveRequest) -> dict:
    chunks = retrieve_context(
        query=payload.query,
        ticker=payload.ticker,
        form_types=payload.form_types,
        top_k=payload.top_k,
    )
    return {"chunks": chunks}

