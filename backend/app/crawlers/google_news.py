"""Google News RSS crawler for public market news discovery."""

from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from xml.etree import ElementTree

import requests

from backend.app.crawlers.base import BaseCrawler
from backend.app.models.schemas import Document, DocumentSummary, SourceRecord, TaskRecord

GOOGLE_NEWS_RSS_URL = (
    "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
)
AUTHORITATIVE_PUBLISHERS = {
    "Reuters",
    "Bloomberg",
    "CNBC",
    "The Wall Street Journal",
    "MarketWatch",
    "Barron's",
    "Yahoo Finance",
    "Financial Times",
    "Seeking Alpha",
    "Investor's Business Daily",
    "The Motley Fool",
}
ANALYST_HINTS = ("UBS", "Goldman Sachs", "Morgan Stanley", "JPMorgan", "Barclays")


class GoogleNewsCrawler(BaseCrawler):
    """Fetch recent public news articles using Google News RSS."""

    key = "google_news_rss"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Query Google News RSS and normalize top items."""
        query = quote_plus(self._build_query(task, source))
        response = requests.get(GOOGLE_NEWS_RSS_URL.format(query=query), timeout=15)
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return []

        documents: list[Document] = []
        for item in channel.findall("item")[:12]:
            raw_title = item.findtext("title", default="Untitled article")
            link = item.findtext("link", default="")
            pub_date = item.findtext("pubDate", default="")
            publisher = item.findtext("source", default="Google News")
            title = self._clean_title(raw_title, publisher)
            published_at = self._parse_pub_date(pub_date)
            if not link:
                continue
            if not self._is_allowed_publisher(publisher):
                continue

            documents.append(
                Document(
                    id=f"{source.code}:{published_at.timestamp()}:{abs(hash(link))}",
                    source_code=source.code,
                    doc_type="article" if source.code == "google_news_analyst" else "news",
                    title=title,
                    company_name=task.query,
                    stock_code=task.query.upper() if len(task.query) <= 6 else None,
                    publish_time=published_at,
                    source_name=publisher,
                    url=link,
                    summary=DocumentSummary(
                        summary_text=self._summary_text(task, source, publisher),
                        key_points=[
                            f"Authoritative publisher: {publisher}.",
                            f"Matched query: {task.query}.",
                            "Open the source article to inspect the original reporting.",
                        ],
                        tags=self._tags_for_source(source),
                    ),
                    attachments=[],
                )
            )
        return documents

    def _build_query(self, task: TaskRecord, source: SourceRecord) -> str:
        """Tailor the Google News query to the requested search type."""
        base = task.query.strip()
        if source.code == "google_news_analyst":
            return f'"{base}" earnings analyst OR upgrade OR downgrade OR price target OR UBS'
        if task.query_type in {"industry", "topic"}:
            return f'"{base}" market OR industry'
        return f'"{base}" earnings OR revenue OR guidance OR market'

    def _clean_title(self, title: str, publisher: str) -> str:
        """Remove the duplicated trailing publisher when present."""
        suffix = f" - {publisher}"
        if title.endswith(suffix):
            return title[: -len(suffix)].strip()
        return title

    def _is_allowed_publisher(self, publisher: str) -> bool:
        """Filter low-authority publishers out of the normalized result set."""
        return any(allowed.lower() in publisher.lower() for allowed in AUTHORITATIVE_PUBLISHERS)

    def _summary_text(self, task: TaskRecord, source: SourceRecord, publisher: str) -> str:
        """Create a cleaner summary message for the UI."""
        if source.code == "google_news_analyst":
            return f"Public analyst-style market commentary from {publisher} for {task.query}."
        return f"Public market coverage from {publisher} for {task.query}."

    def _tags_for_source(self, source: SourceRecord) -> list[str]:
        """Attach result tags aligned with the source intent."""
        if source.code == "google_news_analyst":
            return ["analysis", "analyst-commentary", "public-source"]
        return ["news", "authoritative", "public-source"]

    def _parse_pub_date(self, value: str) -> datetime:
        """Parse RSS pubDate values into aware datetimes."""
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return datetime.now().astimezone()
