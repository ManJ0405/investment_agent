"""Pillar 2 trend-following package."""

from .schemas import Pillar2Input, Pillar2Output, OhlcvCandle


def trend_signal(payload: Pillar2Input) -> Pillar2Output:
    """Lazy-load service dependencies at call time."""
    from .service import trend_signal as _trend_signal

    return _trend_signal(payload)

__all__ = ["OhlcvCandle", "Pillar2Input", "Pillar2Output", "trend_signal"]

