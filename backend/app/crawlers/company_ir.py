"""Company investor-relations crawler for known public-company IR pages."""

from __future__ import annotations

from datetime import datetime

import requests
from bs4 import BeautifulSoup

from backend.app.crawlers.base import BaseCrawler
from backend.app.models.schemas import (
    Document,
    DocumentAttachment,
    DocumentSummary,
    SourceRecord,
    TaskRecord,
)

TESLA_IR_URL = "https://ir.tesla.com/"


class CompanyIRCrawler(BaseCrawler):
    """Fetch earnings-release style materials from known IR pages."""

    key = "company_ir"

    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Dispatch to a supported company IR implementation."""
        normalized = task.query.strip().lower()
        if normalized in {"tesla", "tsla"}:
            return self._collect_tesla_ir(task, source)
        return []

    def _collect_tesla_ir(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Collect Tesla quarterly disclosure links from its IR page."""
        response = requests.get(TESLA_IR_URL, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        filings: list[Document] = []
        seen_urls: set[str] = set()
        current_period = "Latest quarter"

        for link in soup.find_all("a", href=True):
            label = link.get_text(" ", strip=True)
            href = link["href"]
            url = self._absolute_url(href)

            # Track the most recent quarter label when present in surrounding text.
            parent_text = link.parent.get_text(" ", strip=True)
            detected_period = self._extract_period(parent_text)
            if detected_period:
                current_period = detected_period

            if label not in {"Press Release", "Download", "10-Q", "10-K"}:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)

            filings.append(
                self._build_document(
                    source=source,
                    label=label,
                    period=current_period,
                    url=url,
                )
            )

        return filings[:18]

    def _build_document(
        self,
        source: SourceRecord,
        label: str,
        period: str,
        url: str,
    ) -> Document:
        """Convert one Tesla IR link into a normalized document."""
        lower_label = label.lower()
        doc_type = "report" if lower_label in {"download", "10-q", "10-k"} else "article"
        title_map = {
            "download": f"Tesla {period} Shareholder Deck",
            "press release": f"Tesla {period} Earnings Press Release",
            "10-q": f"Tesla {period} Form 10-Q",
            "10-k": f"Tesla {period} Form 10-K",
        }
        title = title_map.get(lower_label, f"Tesla {period} {label}")

        attachments: list[DocumentAttachment] = []
        if lower_label == "download" or url.lower().endswith(".pdf"):
            attachments.append(
                DocumentAttachment(
                    file_type="pdf",
                    file_name=url.rstrip("/").split("/")[-1] or "tesla-ir.pdf",
                    file_url=url,
                )
            )

        return Document(
            id=f"{source.code}:{abs(hash(title + url))}",
            source_code=source.code,
            doc_type=doc_type,
            title=title,
            company_name="Tesla, Inc.",
            stock_code="TSLA",
            publish_time=datetime.now().astimezone(),
            source_name=source.name,
            url=url,
            summary=DocumentSummary(
                summary_text=f"Official Tesla investor-relations material for {period}.",
                key_points=[
                    f"Material type: {label}.",
                    "Primary company investor-relations source.",
                    "Open the source or PDF to inspect the original disclosure.",
                ],
                tags=["investor-relations", "official", "tesla", lower_label.replace(" ", "-")],
            ),
            attachments=attachments,
        )

    def _extract_period(self, text: str) -> str | None:
        """Extract a quarter/year label from nearby text."""
        import re

        match = re.search(r"(Q[1-4]\s+20\d{2}|Q[1-4]|20\d{2})", text)
        if not match:
            return None
        return match.group(1)

    def _absolute_url(self, value: str) -> str:
        """Normalize relative IR links into absolute URLs."""
        if value.startswith("http://") or value.startswith("https://"):
            return value
        return f"https://ir.tesla.com{value if value.startswith('/') else '/' + value}"
