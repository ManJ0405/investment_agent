"""API-backed tools for production-grade Pillar 2 integration."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from langchain.tools import tool
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError
from urllib3.util.retry import Retry

from schemas.ticker_schema import Ohlcv_input, validate_ticker_tool

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_SECONDS = 10.0
_PILLAR2_PATH = "/api/v1/pillars/pillar2/trend-signal"

_http = PoolManager(
    retries=Retry(
        total=2,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["POST"]),
        raise_on_status=False,
    )
)


def _extract_timestamp(row: Dict[str, Any]) -> str:
    raw = row.get("Date") or row.get("date") or row.get("timestamp")
    if raw is None:
        raise ValueError("Missing timestamp field (Date/date/timestamp)")
    if isinstance(raw, datetime):
        return raw.isoformat()
    return str(raw)


def _to_float(value: Any, field_name: str) -> float:
    if value is None:
        raise ValueError(f"Missing required field: {field_name}")
    return float(value)


def _to_api_candles(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    candles: List[Dict[str, Any]] = []
    for row in rows:
        candles.append(
            {
                "timestamp": _extract_timestamp(row),
                "open": _to_float(row.get("Open") if "Open" in row else row.get("open"), "open"),
                "high": _to_float(row.get("High") if "High" in row else row.get("high"), "high"),
                "low": _to_float(row.get("Low") if "Low" in row else row.get("low"), "low"),
                "close": _to_float(row.get("Close") if "Close" in row else row.get("close"), "close"),
                "volume": _to_float(row.get("Volume") if "Volume" in row else row.get("volume"), "volume"),
            }
        )
    return candles


def _pillar2_base_url() -> str:
    return os.getenv("PILLAR2_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _request_pillar2(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{_pillar2_base_url()}{_PILLAR2_PATH}"
    encoded = json.dumps(payload).encode("utf-8")
    try:
        response = _http.request(
            "POST",
            url,
            body=encoded,
            headers={"Content-Type": "application/json"},
            timeout=_DEFAULT_TIMEOUT_SECONDS,
        )
    except HTTPError as exc:
        raise RuntimeError(f"Pillar2 API network error: {exc}") from exc

    text = response.data.decode("utf-8", errors="replace")
    if response.status >= 400:
        raise RuntimeError(f"Pillar2 API HTTP {response.status}: {text[:500]}")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Pillar2 API returned non-JSON response") from exc


@tool(args_schema=Ohlcv_input)
@validate_ticker_tool(schema_class=Ohlcv_input)
def pillar2_trend_signal_api(tickers: List[str], ohlcv: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Call Pillar 2 trend-signal API for each ticker using OHLCV rows.
    Intended for production-style agent integration over service boundaries.
    """
    results: Dict[str, Any] = {}
    for ticker in tickers:
        rows = ohlcv.get(ticker, [])
        if not rows:
            results[ticker] = {"status": "error", "message": f"No OHLCV rows for {ticker}"}
            continue

        try:
            payload = {"ticker": ticker, "candles": _to_api_candles(rows)}
            results[ticker] = {"status": "success", "data": _request_pillar2(payload)}
        except Exception as exc:
            logger.exception("Pillar2 API call failed for %s", ticker)
            results[ticker] = {"status": "error", "message": str(exc)}
    return results

