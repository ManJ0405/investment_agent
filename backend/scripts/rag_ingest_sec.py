"""CLI entrypoint for SEC 10-K/10-Q ingestion into RAG storage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from src.pillars.pillar8_rag.ingest import ingest_filings_for_ticker


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest SEC 10-K/10-Q filings for ticker(s).")
    parser.add_argument("--ticker", action="append", required=True, help="Ticker symbol (repeatable).")
    parser.add_argument("--max-filings", type=int, default=8, help="Max filings per ticker.")
    args = parser.parse_args()

    for ticker in args.ticker:
        result = ingest_filings_for_ticker(ticker=ticker, max_filings=args.max_filings)
        print(result)


if __name__ == "__main__":
    main()

