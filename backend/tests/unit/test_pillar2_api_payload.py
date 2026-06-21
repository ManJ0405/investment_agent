from tools.pillar2_api import _to_api_candles


def test_to_api_candles_maps_title_case_fields():
    rows = [
        {
            "Date": "2026-01-01T00:00:00",
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.5,
            "Volume": 123456,
        }
    ]
    candles = _to_api_candles(rows)
    assert candles[0]["timestamp"] == "2026-01-01T00:00:00"
    assert candles[0]["open"] == 100.0
    assert candles[0]["high"] == 101.0
    assert candles[0]["low"] == 99.0
    assert candles[0]["close"] == 100.5
    assert candles[0]["volume"] == 123456.0


def test_to_api_candles_maps_lower_case_fields():
    rows = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.5,
            "volume": 123456,
        }
    ]
    candles = _to_api_candles(rows)
    assert candles[0]["timestamp"] == "2026-01-01T00:00:00"
    assert candles[0]["open"] == 100.0

