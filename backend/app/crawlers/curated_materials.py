"""Curated fallback materials for companies whose official endpoints are blocked."""

from __future__ import annotations

from datetime import datetime

from backend.app.crawlers.base import BaseCrawler
from backend.app.data.company_profiles import CompanyProfile, resolve_company_profile
from backend.app.models.schemas import (
    Document,
    DocumentAttachment,
    DocumentSummary,
    SourceRecord,
    TaskRecord,
)

CURATED_QUARTERLY_ITEMS: dict[str, list[dict]] = {
    "TSLA": [
        {
            "doc_type": "report",
            "title": "Tesla Q4 and FY 2025 Update",
            "publish_time": "2026-01-28T00:00:00+00:00",
            "url": "https://electrek.co/wp-content/uploads/sites/3/2026/01/TSLA-Q4-2025-Update.pdf",
            "summary": "Quarterly shareholder deck covering Tesla's Q4 and full-year 2025 performance.",
            "tags": ["tesla", "earnings", "shareholder-deck", "pdf-mirror"],
            "attachments": [
                {
                    "file_type": "pdf",
                    "file_name": "TSLA-Q4-2025-Update.pdf",
                    "file_url": "https://electrek.co/wp-content/uploads/sites/3/2026/01/TSLA-Q4-2025-Update.pdf",
                }
            ],
        },
        {
            "doc_type": "article",
            "title": "Tesla Releases Fourth Quarter and Full Year 2025 Financial Results",
            "publish_time": "2026-01-28T00:00:00+00:00",
            "url": "https://ir.tesla.com/press-release/tesla-releases-fourth-quarter-and-full-year-2025-financial-results",
            "summary": "Official Tesla IR release announcing the quarter-end financial results and webcast.",
            "tags": ["tesla", "official-release", "earnings"],
            "attachments": [],
        },
        {
            "doc_type": "report",
            "title": "Tesla Q3 2025 Update",
            "publish_time": "2025-10-22T00:00:00+00:00",
            "url": "https://electrek.co/wp-content/uploads/sites/3/2025/10/TSLA-Q3-2025-Update.pdf",
            "summary": "Quarterly shareholder deck covering Tesla's Q3 2025 performance.",
            "tags": ["tesla", "earnings", "shareholder-deck", "pdf-mirror"],
            "attachments": [
                {
                    "file_type": "pdf",
                    "file_name": "TSLA-Q3-2025-Update.pdf",
                    "file_url": "https://electrek.co/wp-content/uploads/sites/3/2025/10/TSLA-Q3-2025-Update.pdf",
                }
            ],
        },
        {
            "doc_type": "article",
            "title": "Tesla Releases Third Quarter 2025 Financial Results",
            "publish_time": "2025-10-22T00:00:00+00:00",
            "url": "https://ir.tesla.com/press-release/tesla-releases-third-quarter-2025-financial-results",
            "summary": "Official Tesla IR release announcing the quarter-end financial results and webcast.",
            "tags": ["tesla", "official-release", "earnings"],
            "attachments": [],
        },
        {
            "doc_type": "report",
            "title": "Tesla Q2 2025 Update",
            "publish_time": "2025-07-23T00:00:00+00:00",
            "url": "https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf",
            "summary": "Quarterly shareholder deck covering Tesla's Q2 2025 performance.",
            "tags": ["tesla", "earnings", "shareholder-deck", "official-pdf"],
            "attachments": [
                {
                    "file_type": "pdf",
                    "file_name": "TSLA-Q2-2025-Update.pdf",
                    "file_url": "https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf",
                }
            ],
        },
        {
            "doc_type": "article",
            "title": "Tesla Releases Second Quarter 2025 Financial Results",
            "publish_time": "2025-07-23T00:00:00+00:00",
            "url": "https://ir.tesla.com/press-release/tesla-releases-second-quarter-2025-financial-results",
            "summary": "Official Tesla IR release announcing the quarter-end financial results and webcast.",
            "tags": ["tesla", "official-release", "earnings"],
            "attachments": [],
        },
        {
            "doc_type": "report",
            "title": "Tesla Q1 2025 Update",
            "publish_time": "2025-04-22T00:00:00+00:00",
            "url": "https://electrek.co/wp-content/uploads/sites/3/2025/04/TSLA-Q1-2025-Update.pdf",
            "summary": "Quarterly shareholder deck covering Tesla's Q1 2025 performance.",
            "tags": ["tesla", "earnings", "shareholder-deck", "pdf-mirror"],
            "attachments": [
                {
                    "file_type": "pdf",
                    "file_name": "TSLA-Q1-2025-Update.pdf",
                    "file_url": "https://electrek.co/wp-content/uploads/sites/3/2025/04/TSLA-Q1-2025-Update.pdf",
                }
            ],
        },
        {
            "doc_type": "article",
            "title": "Tesla Releases First Quarter 2025 Financial Results",
            "publish_time": "2025-04-22T00:00:00+00:00",
            "url": "https://ir.tesla.com/press-release/tesla-releases-first-quarter-2025-financial-results",
            "summary": "Official Tesla IR release announcing the quarter-end financial results and webcast.",
            "tags": ["tesla", "official-release", "earnings"],
            "attachments": [],
        },
    ]
}


class CuratedMaterialsCrawler(BaseCrawler):
    """Return scalable fallback materials for known companies."""

    key = "curated_materials"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Return company profile pages plus curated quarter-specific materials."""
        profile = resolve_company_profile(task.query)
        if profile is None:
            return []

        documents = self._build_company_pack(profile, source)
        for item in CURATED_QUARTERLY_ITEMS.get(profile.ticker, []):
            documents.append(self._build_quarterly_document(profile, source, item))
        return documents

    def _build_company_pack(
        self, profile: CompanyProfile, source: SourceRecord
    ) -> list[Document]:
        """Build a reusable base pack for supported companies."""
        documents = [
            self._build_document(
                source=source,
                profile=profile,
                title=f"{profile.company_name} Investor Relations",
                doc_type="article",
                url=profile.ir_url,
                publish_time=datetime.now().astimezone(),
                summary_text="Official investor-relations hub used as the primary source of company disclosures.",
                tags=["official", "investor-relations", profile.ticker.lower()],
                attachments=[],
            ),
            self._build_document(
                source=source,
                profile=profile,
                title=f"{profile.company_name} Earnings and Results",
                doc_type="report",
                url=profile.results_url or profile.ir_url,
                publish_time=datetime.now().astimezone(),
                summary_text="Official results or press-release page for quarterly and annual updates.",
                tags=["official", "earnings", "results-page", profile.ticker.lower()],
                attachments=[],
            ),
            self._build_document(
                source=source,
                profile=profile,
                title=f"{profile.company_name} Filings and Disclosures",
                doc_type="report",
                url=profile.results_url or profile.ir_url,
                publish_time=datetime.now().astimezone(),
                summary_text=(
                    "Official company results or disclosure page used as a more stable fallback "
                    "when direct SEC access is blocked in the current network."
                ),
                tags=["official", "disclosures", "results-page", profile.ticker.lower()],
                attachments=[
                    DocumentAttachment(
                        file_type="link",
                        file_name=f"{profile.ticker.lower()}-sec-browser",
                        file_url=(
                            "https://www.sec.gov/cgi-bin/browse-edgar"
                            f"?action=getcompany&CIK={profile.ticker}&owner=exclude&count=40"
                        ),
                    )
                ],
            ),
        ]
        return documents

    def _build_quarterly_document(
        self,
        profile: CompanyProfile,
        source: SourceRecord,
        item: dict,
    ) -> Document:
        """Build one quarter-specific curated material."""
        attachments = [DocumentAttachment(**attachment) for attachment in item["attachments"]]
        return self._build_document(
            source=source,
            profile=profile,
            title=item["title"],
            doc_type=item["doc_type"],
            url=item["url"],
            publish_time=datetime.fromisoformat(item["publish_time"]),
            summary_text=item["summary"],
            tags=item["tags"],
            attachments=attachments,
        )

    def _build_document(
        self,
        source: SourceRecord,
        profile: CompanyProfile,
        title: str,
        doc_type: str,
        url: str,
        publish_time: datetime,
        summary_text: str,
        tags: list[str],
        attachments: list[DocumentAttachment],
    ) -> Document:
        """Normalize a curated company material into the shared schema."""
        return Document(
            id=f"{source.code}:{abs(hash(title + url))}",
            source_code=source.code,
            doc_type=doc_type,
            title=title,
            company_name=profile.company_name,
            stock_code=profile.ticker,
            publish_time=publish_time,
            source_name=source.name,
            url=url,
            summary=DocumentSummary(
                summary_text=summary_text,
                key_points=[
                    "Fallback material used when direct official endpoints are blocked.",
                    "Prioritizes official investor-relations and browser-openable filing pages.",
                    "Use together with analyst coverage and market news for context.",
                ],
                tags=tags,
            ),
            attachments=attachments,
        )
