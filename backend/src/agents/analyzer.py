import logging
from langchain_core.messages import AIMessage
from tools.analysis import mean_reversion
from tools.pillar2_api import pillar2_trend_signal_api

logger = logging.getLogger(__name__)

def analyzer_node(state):
    """Run full deterministic analysis over fetched ticker data."""
    logger.info(
        "analyzer_node: in (messages=%d, has_analysis=%s)",
        len(state.get("messages", [])),
        bool(state.get("analysis_result")),
    )

    fetched = state.get("fetched_data") or {}
    tickers = fetched.get("tickers") or []
    ohlcv = fetched.get("ohlcv") or {}
    fundamentals = fetched.get("fundamentals") or []

    if not tickers or not ohlcv:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "I could not find usable fetched OHLCV data to analyze. "
                        "Please ask for a specific ticker, for example: `Analyze NVDA`."
                    )
                )
            ],
            "analysis_result": {"completed": False, "reason": "missing_data"},
        }

    mean_resp = mean_reversion.invoke({"tickers": tickers, "ohlcv": ohlcv})
    pillar2_resp = pillar2_trend_signal_api.invoke({"tickers": tickers, "ohlcv": ohlcv})

    mean_data = mean_resp.get("data", {}) if isinstance(mean_resp, dict) else {}
    pillar2_data = pillar2_resp.get("data", {}) if isinstance(pillar2_resp, dict) else {}

    fundamentals_by_ticker = {}
    if isinstance(fundamentals, list):
        for item in fundamentals:
            ticker = item.get("ticker")
            if ticker:
                fundamentals_by_ticker[ticker] = item

    per_ticker = {}
    for ticker in tickers:
        rows = ohlcv.get(ticker) or []
        latest_close = None
        if isinstance(rows, list) and rows:
            latest_row = rows[-1]
            latest_close = latest_row.get("Close") if "Close" in latest_row else latest_row.get("close")

        p2_entry = pillar2_data.get(ticker, {})
        p2 = p2_entry.get("data") if isinstance(p2_entry, dict) and p2_entry.get("status") == "success" else None
        mean_rev = mean_data.get(ticker, {}) if isinstance(mean_data, dict) else {}
        funda_item = fundamentals_by_ticker.get(ticker, {})
        latest_funda = (funda_item.get("data") or [None])[0] if isinstance(funda_item, dict) else None

        per_ticker[ticker] = {
            "latest_close": latest_close,
            "pillar2": p2,
            "mean_reversion": mean_rev,
            "latest_fundamental": latest_funda,
            "news_count": len(funda_item.get("news") or []) if isinstance(funda_item, dict) else 0,
        }

    completed_count = sum(1 for t in per_ticker.values() if t.get("latest_close") is not None)
    summary = f"Completed full analysis for {completed_count}/{len(tickers)} ticker(s): {', '.join(tickers)}."

    return {
        "messages": [AIMessage(content=summary)],
        "analysis_result": {
            "completed": True,
            "tickers": tickers,
            "per_ticker": per_ticker,
        },
    }
