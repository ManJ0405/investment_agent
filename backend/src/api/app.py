"""FastAPI app exposing production-style endpoints."""

from fastapi import FastAPI

try:
    from src.pillars.pillar2_trend import Pillar2Input, Pillar2Output, trend_signal
except ModuleNotFoundError:
    from pillars.pillar2_trend import Pillar2Input, Pillar2Output, trend_signal

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

