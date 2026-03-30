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


class GoogleNewsCrawler(BaseCrawler):
    """Fetch recent public news articles using Google News RSS."""

    key = "google_news_rss"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Query Google News RSS and normalize top items."""
        query = quote_plus(f"{task.query} stock market")
        response = requests.get(GOOGLE_NEWS_RSS_URL.format(query=query), timeout=15)
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return []

        documents: list[Document] = []
        for item in channel.findall("item")[:12]:
            title = item.findtext("title", default="Untitled article")
            link = item.findtext("link", default="")
            pub_date = item.findtext("pubDate", default="")
            published_at = self._parse_pub_date(pub_date)
            if not link:
                continue

            documents.append(
                Document(
                    id=f"{source.code}:{published_at.timestamp()}:{abs(hash(link))}",
                    source_code=source.code,
                    doc_type="article",
                    title=title,
                    company_name=task.query,
                    stock_code=task.query.upper() if len(task.query) <= 6 else None,
                    publish_time=published_at,
                    source_name=source.name,
                    url=link,
                    summary=DocumentSummary(
                        summary_text=(
                            "Public news coverage discovered through Google News RSS."
                        ),
                        key_points=[
                            "Real-time public article source.",
                            f"Matched query: {task.query}.",
                            "Open the source article to inspect the original reporting.",
                        ],
                        tags=["news", "google-news", "public-source"],
                    ),
                    attachments=[],
                )
            )
        return documents

    def _parse_pub_date(self, value: str) -> datetime:
        """Parse RSS pubDate values into aware datetimes."""
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return datetime.now().astimezone()
