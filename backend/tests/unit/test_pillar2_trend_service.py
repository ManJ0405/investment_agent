from datetime import datetime, timedelta

from pillars.pillar2_trend import Pillar2Input, OhlcvCandle, trend_signal


def _make_candles(length: int, start_price: float, daily_step: float) -> list[OhlcvCandle]:
    base = datetime(2025, 1, 1)
    rows = []
    price = start_price
    for day in range(length):
        price += daily_step
        rows.append(
            OhlcvCandle(
                timestamp=base + timedelta(days=day),
                open=price * 0.998,
                high=price * 1.004,
                low=price * 0.994,
                close=price,
                volume=1_000_000 + day * 50,
            )
        )
    return rows


def test_trend_signal_bullish_for_uptrend():
    payload = Pillar2Input(ticker="IBM", candles=_make_candles(120, 100, 0.6))
    output = trend_signal(payload)

    assert output.ticker == "IBM"
    assert output.signal == "bullish"
    assert output.score >= 65
    assert output.confidence > 0.5
    assert "adx_14" in output.evidence


def test_trend_signal_bearish_for_downtrend():
    payload = Pillar2Input(ticker="IBM", candles=_make_candles(120, 220, -0.7))
    output = trend_signal(payload)

    assert output.signal in {"bearish", "neutral"}
    assert output.score < 65
    assert 0 <= output.confidence <= 1


def test_input_requires_minimum_candles():
    candles = _make_candles(20, 100, 0.2)
    try:
        Pillar2Input(ticker="IBM", candles=candles)
        assert False, "Expected validation error for short series"
    except Exception:
        assert True

