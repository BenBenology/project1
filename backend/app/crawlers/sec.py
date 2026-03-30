"""SEC EDGAR crawler backed by official SEC JSON APIs."""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache

import requests

from backend.app.crawlers.base import BaseCrawler
from backend.app.core.config import get_settings
from backend.app.models.schemas import Document, DocumentSummary, SourceRecord, TaskRecord
from backend.app.crawlers.sec_seed import FALLBACK_COMPANIES

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"
REPORT_FORMS = {"10-K", "10-Q", "20-F", "40-F"}


class SecSubmissionsCrawler(BaseCrawler):
    """Fetch official SEC filings for a ticker or company query."""

    key = "sec_submissions"

    def __init__(self) -> None:
        settings = get_settings()
        self._headers = {
            "User-Agent": settings.sec_user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Resolve the query and fetch recent SEC submissions."""
        company = self._resolve_company(task.query)
        if company is None:
            return []

        cik = str(company["cik_str"]).zfill(10)
        response = requests.get(
            SEC_SUBMISSIONS_URL.format(cik=cik),
            headers=self._headers,
            timeout=15,
        )
        response.raise_for_status()
        return self._build_documents(
            submissions=response.json(),
            source=source,
            company_name=company["title"],
            stock_code=company["ticker"],
        )

    @lru_cache(maxsize=1)
    def _ticker_map(self) -> list[dict]:
        """Load and cache SEC's public ticker mapping."""
        try:
            response = requests.get(SEC_TICKERS_URL, headers=self._headers, timeout=15)
            response.raise_for_status()
            payload = response.json()
            return list(payload.values()) if isinstance(payload, dict) else payload
        except requests.RequestException:
            # Keep common large-cap tickers usable when the SEC ticker file is flaky.
            return FALLBACK_COMPANIES

    def _resolve_company(self, query: str) -> dict | None:
        """Resolve a ticker or company name against SEC's official list."""
        normalized = query.strip().lower()
        for company in self._ticker_map():
            ticker = str(company.get("ticker", "")).lower()
            title = str(company.get("title", "")).lower()
            if normalized == ticker or normalized == title:
                return company

        for company in self._ticker_map():
            ticker = str(company.get("ticker", "")).lower()
            title = str(company.get("title", "")).lower()
            if normalized in ticker or normalized in title:
                return company
        return None

    def _build_documents(
        self,
        submissions: dict,
        source: SourceRecord,
        company_name: str,
        stock_code: str,
    ) -> list[Document]:
        """Normalize recent SEC filings into the shared document schema."""
        recent = submissions.get("filings", {}).get("recent", {})
        accession_numbers = recent.get("accessionNumber", [])
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        primary_documents = recent.get("primaryDocument", [])

        documents: list[Document] = []
        for index, accession in enumerate(accession_numbers[:20]):
            form = forms[index] if index < len(forms) else ""
            filing_date = filing_dates[index] if index < len(filing_dates) else None
            primary_document = (
                primary_documents[index] if index < len(primary_documents) else ""
            )
            if not form or not filing_date or not primary_document:
                continue

            accession_no_dashes = accession.replace("-", "")
            cik_without_leading_zeros = str(int(submissions["cik"]))
            filing_url = (
                f"{SEC_ARCHIVES_BASE}/{cik_without_leading_zeros}/"
                f"{accession_no_dashes}/{primary_document}"
            )
            documents.append(
                Document(
                    id=f"{source.code}:{accession}",
                    source_code=source.code,
                    doc_type="report" if form in REPORT_FORMS else "filing",
                    title=f"{company_name} {form} filed on {filing_date}",
                    company_name=company_name,
                    stock_code=stock_code,
                    publish_time=datetime.fromisoformat(f"{filing_date}T00:00:00+00:00"),
                    source_name=source.name,
                    url=filing_url,
                    summary=DocumentSummary(
                        summary_text=self._summary_text(form, filing_date),
                        key_points=[
                            f"Official SEC filing type: {form}.",
                            f"Filed on {filing_date}.",
                            "Open the filing to inspect full disclosure details.",
                        ],
                        tags=["sec", "official", form.lower()],
                    ),
                    attachments=[],
                )
            )
        return documents

    def _summary_text(self, form: str, filing_date: str) -> str:
        """Build a short human-readable filing summary."""
        if form in REPORT_FORMS:
            return f"Official {form} filing published through SEC EDGAR on {filing_date}."
        return f"Official {form} disclosure published through SEC EDGAR on {filing_date}."
