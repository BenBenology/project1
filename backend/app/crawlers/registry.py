"""Registry mapping source definitions to crawler implementations."""

from __future__ import annotations

from backend.app.crawlers.base import BaseCrawler
from backend.app.crawlers.google_news import GoogleNewsCrawler
from backend.app.crawlers.mock import MockFinancialCrawler, MockNewsCrawler
from backend.app.crawlers.sec import SecSubmissionsCrawler
from backend.app.models.schemas import SourceRecord


class CrawlerRegistry:
    """Look up crawlers by key and dispatch collection calls."""

    def __init__(self) -> None:
        self._crawlers: dict[str, BaseCrawler] = {}
        self.register(GoogleNewsCrawler())
        self.register(SecSubmissionsCrawler())
        self.register(MockFinancialCrawler())
        self.register(MockNewsCrawler())

    def register(self, crawler: BaseCrawler) -> None:
        """Add a crawler implementation to the registry."""
        self._crawlers[crawler.key] = crawler

    def get(self, crawler_key: str) -> BaseCrawler:
        """Return a crawler for the provided key."""
        crawler = self._crawlers.get(crawler_key)
        if crawler is None:
            raise KeyError(f"Unknown crawler key: {crawler_key}")
        return crawler

    def enabled_keys(self) -> list[str]:
        """Expose registered crawler keys for validation/debugging."""
        return sorted(self._crawlers.keys())


crawler_registry = CrawlerRegistry()
