"""Core deterministic scoring logic for Pillar 2."""

from __future__ import annotations

import time

import pandas as pd
import pandas_ta as ta

from .schemas import Pillar2Input, Pillar2Output


def _safe_float(value: float | int | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    return float(value)


def _build_feature_frame(payload: Pillar2Input) -> pd.DataFrame:
    frame = pd.DataFrame([c.model_dump() for c in payload.candles]).sort_values("timestamp")
    frame["ema_fast"] = ta.ema(frame["close"], length=20)
    frame["ema_slow"] = ta.ema(frame["close"], length=50)
    frame["adx"] = ta.adx(frame["high"], frame["low"], frame["close"], length=14)["ADX_14"]
    frame["atr"] = ta.atr(frame["high"], frame["low"], frame["close"], length=14)
    frame["atr_pct"] = frame["atr"] / frame["close"]
    return frame


def trend_signal(payload: Pillar2Input) -> Pillar2Output:
    """Return a stable trend score with confidence and evidence."""
    started = time.perf_counter()

    frame = _build_feature_frame(payload)
    latest = frame.iloc[-1]
    previous = frame.iloc[-2]

    close = _safe_float(latest["close"])
    ema_fast = _safe_float(latest["ema_fast"], close)
    ema_slow = _safe_float(latest["ema_slow"], close)
    adx = _safe_float(latest["adx"])
    atr_pct = _safe_float(latest["atr_pct"])

    ema_spread_ratio = (ema_fast - ema_slow) / ema_slow if ema_slow else 0.0
    ema_slope = _safe_float(latest["ema_fast"]) - _safe_float(previous["ema_fast"])

    trend_direction = 1.0 if ema_spread_ratio > 0 else (-1.0 if ema_spread_ratio < 0 else 0.0)
    slope_direction = 1.0 if ema_slope > 0 else (-1.0 if ema_slope < 0 else 0.0)
    direction_alignment = 1.0 if trend_direction == slope_direction else 0.4

    trend_component = 50.0 + (18.0 * trend_direction)
    strength_component = min(max(adx, 0.0), 50.0) * 0.45 * trend_direction * direction_alignment
    momentum_component = (
        10.0 * trend_direction
        if trend_direction != 0 and slope_direction == trend_direction
        else -4.0 * trend_direction
    )

    # Penalize unstable high-volatility regimes.
    volatility_penalty = max((atr_pct - 0.04) * 400.0, 0.0)

    score = max(0.0, min(100.0, trend_component + strength_component + momentum_component - volatility_penalty))

    if score >= 65:
        signal = "bullish"
    elif score <= 35:
        signal = "bearish"
    else:
        signal = "neutral"

    confidence = 0.45 + min(adx / 100.0, 0.35) + (0.15 if atr_pct < 0.05 else 0.0)
    confidence = max(0.0, min(1.0, confidence))

    elapsed = int((time.perf_counter() - started) * 1000)
    evidence = {
        "close": round(close, 4),
        "ema_fast": round(ema_fast, 4),
        "ema_slow": round(ema_slow, 4),
        "ema_spread_ratio": round(ema_spread_ratio, 6),
        "ema_fast_slope": round(ema_slope, 6),
        "trend_direction": "up" if trend_direction > 0 else ("down" if trend_direction < 0 else "flat"),
        "adx_14": round(adx, 4),
        "atr_pct_14": round(atr_pct, 6),
        "volatility_penalty": round(volatility_penalty, 4),
    }

    return Pillar2Output(
        ticker=payload.ticker,
        signal=signal,
        score=round(score, 3),
        confidence=round(confidence, 3),
        evidence=evidence,
        latency_ms=elapsed,
    )

