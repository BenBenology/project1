"""Mock crawler implementations that emulate different source families."""

from __future__ import annotations

from backend.app.crawlers.base import BaseCrawler
from backend.app.models.schemas import Document, SourceRecord, TaskRecord
from backend.app.services.mock_data import build_mock_documents


class MockFinancialCrawler(BaseCrawler):
    """Emit financial-report style mock documents."""

    key = "mock_financial"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Return report and filing documents for the configured source."""
        documents = build_mock_documents(task.query, source_code=source.code)
        return [doc for doc in documents if doc.doc_type in {"report", "filing"}]


class MockNewsCrawler(BaseCrawler):
    """Emit news/article style mock documents."""

    key = "mock_news"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Return news and article documents for the configured source."""
        documents = build_mock_documents(task.query, source_code=source.code)
        return [doc for doc in documents if doc.doc_type in {"news", "article"}]

