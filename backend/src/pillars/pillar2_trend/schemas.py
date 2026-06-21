"""Schemas for Pillar 2 trend signal scoring."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class OhlcvCandle(BaseModel):
    """Single OHLCV row for one timestamp."""

    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @field_validator("high")
    @classmethod
    def high_must_be_max(cls, value: float, info: ValidationInfo) -> float:
        low = info.data.get("low")
        open_ = info.data.get("open")
        close = info.data.get("close")
        if low is not None and value < low:
            raise ValueError("high must be >= low")
        if open_ is not None and value < open_:
            raise ValueError("high must be >= open")
        if close is not None and value < close:
            raise ValueError("high must be >= close")
        return value

    @field_validator("low")
    @classmethod
    def low_must_be_min(cls, value: float, info: ValidationInfo) -> float:
        high = info.data.get("high")
        open_ = info.data.get("open")
        close = info.data.get("close")
        if high is not None and value > high:
            raise ValueError("low must be <= high")
        if open_ is not None and value > open_:
            raise ValueError("low must be <= open")
        if close is not None and value > close:
            raise ValueError("low must be <= close")
        return value


class Pillar2Input(BaseModel):
    """Request payload for trend scoring."""

    ticker: str = Field(min_length=1, max_length=20)
    candles: list[OhlcvCandle] = Field(min_length=60, description="At least 60 bars")


class Pillar2Output(BaseModel):
    """Deterministic trend scoring output."""

    ticker: str
    signal: Literal["bullish", "neutral", "bearish"]
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    evidence: dict[str, float | str]
    latency_ms: int = Field(ge=0)

