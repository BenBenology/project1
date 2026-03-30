"""Curated fallback materials for companies whose official endpoints are blocked."""

from __future__ import annotations

from datetime import datetime

from backend.app.crawlers.base import BaseCrawler
from backend.app.models.schemas import (
    Document,
    DocumentAttachment,
    DocumentSummary,
    SourceRecord,
    TaskRecord,
)

TESLA_CURATED_ITEMS = [
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


class CuratedMaterialsCrawler(BaseCrawler):
    """Return carefully selected fallback materials when direct crawling is blocked."""

    key = "curated_materials"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Return curated fallback materials for supported companies."""
        normalized = task.query.strip().lower()
        if normalized not in {"tesla", "tsla"}:
            return []

        documents: list[Document] = []
        for item in TESLA_CURATED_ITEMS:
            attachments = [
                DocumentAttachment(**attachment) for attachment in item["attachments"]
            ]
            documents.append(
                Document(
                    id=f"{source.code}:{abs(hash(item['title'] + item['url']))}",
                    source_code=source.code,
                    doc_type=item["doc_type"],
                    title=item["title"],
                    company_name="Tesla, Inc.",
                    stock_code="TSLA",
                    publish_time=datetime.fromisoformat(item["publish_time"]),
                    source_name=source.name,
                    url=item["url"],
                    summary=DocumentSummary(
                        summary_text=item["summary"],
                        key_points=[
                            "Fallback material used when direct official endpoints are blocked.",
                            "Includes an official release page or a directly openable PDF deck.",
                            "Use together with analyst coverage and market news for context.",
                        ],
                        tags=item["tags"],
                    ),
                    attachments=attachments,
                )
            )
        return documents
