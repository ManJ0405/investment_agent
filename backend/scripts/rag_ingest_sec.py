"""CLI entrypoint for SEC 10-K/10-Q ingestion into RAG storage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pytickersymbols import PyTickerSymbols

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from src.pillars.pillar8_rag.ingest import ingest_filings_for_ticker

SP500_INDEX = "S&P 500"


def get_sp500_tickers() -> list[str]:
    """Return current S&P 500 constituent tickers (uppercase, deduplicated)."""
    stock_data = PyTickerSymbols()
    symbols = [item["symbol"].upper() for item in stock_data.get_stocks_by_index(SP500_INDEX)]
    return list(dict.fromkeys(symbols))


def ingest_sp500_filings(
    max_filings: int = 8,
    limit: int | None = None,
) -> dict[str, object]:
    """Ingest SEC filings for all S&P 500 tickers into the vector DB."""
    tickers = get_sp500_tickers()
    if limit is not None:
        tickers = tickers[:limit]

    succeeded: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []

    for idx, ticker in enumerate(tickers, start=1):
        print(f"[{idx}/{len(tickers)}] Ingesting {ticker}...")
        try:
            result = ingest_filings_for_ticker(ticker=ticker, max_filings=max_filings)
            succeeded.append(result)
            print(result)
        except Exception as exc:
            failed.append({"ticker": ticker, "error": str(exc)})
            print(f"Failed {ticker}: {exc}")

    return {
        "index": SP500_INDEX,
        "tickers_requested": len(tickers),
        "tickers_succeeded": len(succeeded),
        "tickers_failed": len(failed),
        "filings_ingested": sum(int(r["filings_ingested"]) for r in succeeded),
        "failed": failed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest SEC 10-K/10-Q filings for ticker(s).")
    parser.add_argument("--ticker", action="append", help="Ticker symbol (repeatable).")
    parser.add_argument("--sp500", action="store_true", help="Ingest all S&P 500 constituents.")
    parser.add_argument("--max-filings", type=int, default=8, help="Max filings per ticker.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="When using --sp500, only ingest the first N tickers (useful for testing).",
    )
    args = parser.parse_args()

    if args.sp500:
        summary = ingest_sp500_filings(max_filings=args.max_filings, limit=args.limit)
        print(summary)
        return

    if not args.ticker:
        parser.error("Provide --ticker (repeatable) or use --sp500.")

    for ticker in args.ticker:
        result = ingest_filings_for_ticker(ticker=ticker, max_filings=args.max_filings)
        print(result)


if __name__ == "__main__":
    main()

