"""SEC EDGAR client for company/ticker metadata and filings."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from urllib3 import PoolManager
from urllib3.util.retry import Retry


SEC_BASE = "https://www.sec.gov"
SEC_DATA_BASE = "https://data.sec.gov"
ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"


def _user_agent() -> str:
    # SEC requests a descriptive User-Agent with contact details.
    contact = os.getenv("SEC_API_USER_AGENT", "investment-agent/0.1 (mandes2003@gmail.com)")
    return contact


@dataclass
class FilingRecord:
    cik: str
    ticker: str
    company_name: str
    accession_no: str
    form_type: str
    filing_date: str
    report_date: str | None
    primary_doc: str

    @property
    def cik_int(self) -> str:
        return str(int(self.cik))

    @property
    def accession_no_compact(self) -> str:
        return self.accession_no.replace("-", "")

    @property
    def filing_url(self) -> str:
        return f"{ARCHIVES_BASE}/{self.cik_int}/{self.accession_no_compact}/{self.primary_doc}"


class SecClient:
    def __init__(self) -> None:
        self.http = PoolManager(
            retries=Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset({"GET"}),
            ),
            headers={
                "User-Agent": _user_agent(),
                "Accept": "application/json, text/html;q=0.9",
            },
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        response = self.http.request("GET", url, timeout=30.0)
        if response.status >= 400:
            raise RuntimeError(f"SEC request failed {response.status}: {url}")
        return json.loads(response.data.decode("utf-8"))

    def get_company_tickers(self) -> list[dict[str, str]]:
        data = self._get_json(f"{SEC_BASE}/files/company_tickers.json")
        rows = []
        for _, item in data.items():
            rows.append(
                {
                    "ticker": str(item.get("ticker", "")).upper(),
                    "company_name": str(item.get("title", "")),
                    "cik": str(item.get("cik_str", "")).zfill(10),
                }
            )
        return rows

    def get_company_by_ticker(self, ticker: str) -> dict[str, str] | None:
        ticker = ticker.upper().strip()
        for row in self.get_company_tickers():
            if row["ticker"] == ticker:
                return row
        return None

    def get_recent_filings(self, cik: str, ticker: str, company_name: str) -> list[FilingRecord]:
        cik = str(cik).zfill(10)
        data = self._get_json(f"{SEC_DATA_BASE}/submissions/CIK{cik}.json")
        recent = data.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        primary_docs = recent.get("primaryDocument", [])

        out: list[FilingRecord] = []
        for i, form in enumerate(forms):
            if form not in {"10-K", "10-Q"}:
                continue
            out.append(
                FilingRecord(
                    cik=cik,
                    ticker=ticker,
                    company_name=company_name,
                    accession_no=accession_numbers[i],
                    form_type=form,
                    filing_date=filing_dates[i],
                    report_date=report_dates[i] if i < len(report_dates) else None,
                    primary_doc=primary_docs[i],
                )
            )
        return out

    def fetch_filing_text(self, filing: FilingRecord) -> str:
        response = self.http.request("GET", filing.filing_url, timeout=45.0)
        if response.status >= 400:
            raise RuntimeError(f"Failed to fetch filing document {response.status}: {filing.filing_url}")
        raw = response.data.decode("utf-8", errors="ignore")
        # Simple html strip for baseline ingestion.
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

