from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from api.app import app


def _payload(length: int = 80) -> dict:
    base = datetime(2025, 1, 1)
    candles = []
    price = 100.0
    for day in range(length):
        price += 0.45
        candles.append(
            {
                "timestamp": (base + timedelta(days=day)).isoformat(),
                "open": round(price * 0.998, 6),
                "high": round(price * 1.004, 6),
                "low": round(price * 0.994, 6),
                "close": round(price, 6),
                "volume": 1_000_000 + day * 100,
            }
        )
    return {"ticker": "NVDA", "candles": candles}


def test_healthz_ok():
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pillar2_route_returns_scored_output():
    client = TestClient(app)
    response = client.post("/api/v1/pillars/pillar2/trend-signal", json=_payload())
    assert response.status_code == 200
    body = response.json()

    assert body["ticker"] == "NVDA"
    assert body["signal"] in {"bullish", "neutral", "bearish"}
    assert 0 <= body["score"] <= 100
    assert 0 <= body["confidence"] <= 1
    assert "evidence" in body and isinstance(body["evidence"], dict)
    assert "latency_ms" in body

