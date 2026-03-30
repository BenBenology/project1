"""Mock data builder for reports and article results."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.app.models.schemas import Document, DocumentAttachment, DocumentSummary


def build_mock_documents(query: str, source_code: str | None = None) -> list[Document]:
    """Generate deterministic example documents for the submitted query."""
    query_upper = query.upper()
    company_name = query if len(query) > 3 else f"{query_upper} Holdings"
    now = datetime.now(UTC)
    source_value = source_code or "mock"

    return [
        Document(
            id=f"{query_lower_safe(query)}-report-q4",
            source_code=source_value,
            doc_type="report",
            title=f"{company_name} Q4 2025 Earnings Report",
            company_name=company_name,
            stock_code=query_upper if len(query) <= 5 else None,
            publish_time=now - timedelta(days=7),
            source_name="Official IR",
            url=f"https://example.com/{query_lower_safe(query)}/q4-report",
            summary=DocumentSummary(
                summary_text="Revenue and margin both improved, driven by core product growth.",
                key_points=[
                    "Revenue grew year over year.",
                    "Gross margin expanded.",
                    "Management issued a positive near-term outlook.",
                ],
                tags=["financial-report", "earnings", "official"],
            ),
            attachments=[
                DocumentAttachment(
                    file_type="pdf",
                    file_name=f"{query_upper}_Q4_2025_Report.pdf",
                    file_url=f"https://example.com/files/{query_lower_safe(query)}-q4-2025.pdf",
                )
            ],
        ),
        Document(
            id=f"{query_lower_safe(query)}-filing-10k",
            source_code=source_value,
            doc_type="filing",
            title=f"{company_name} Annual Filing 2025",
            company_name=company_name,
            stock_code=query_upper if len(query) <= 5 else None,
            publish_time=now - timedelta(days=10),
            source_name="Regulatory Filing",
            url=f"https://example.com/{query_lower_safe(query)}/annual-filing",
            summary=DocumentSummary(
                summary_text="The annual filing highlights strategy, risk factors, and segment performance.",
                key_points=[
                    "Risk disclosures updated.",
                    "Regional performance was mixed.",
                    "Capex increased to support future expansion.",
                ],
                tags=["filing", "annual-report", "compliance"],
            ),
            attachments=[
                DocumentAttachment(
                    file_type="pdf",
                    file_name=f"{query_upper}_Annual_Filing_2025.pdf",
                    file_url=f"https://example.com/files/{query_lower_safe(query)}-annual-filing.pdf",
                )
            ],
        ),
        Document(
            id=f"{query_lower_safe(query)}-news-supply-chain",
            source_code=source_value,
            doc_type="news",
            title=f"{company_name} Expands Supply Chain Capacity",
            company_name=company_name,
            stock_code=query_upper if len(query) <= 5 else None,
            publish_time=now - timedelta(days=2),
            source_name="Market News Daily",
            url=f"https://example.com/news/{query_lower_safe(query)}-supply-chain",
            summary=DocumentSummary(
                summary_text="A new manufacturing partnership may improve shipment stability next quarter.",
                key_points=[
                    "New partner announced.",
                    "Capacity expansion targets next quarter.",
                    "Analysts expect improved delivery resilience.",
                ],
                tags=["news", "operations", "supply-chain"],
            ),
            attachments=[],
        ),
        Document(
            id=f"{query_lower_safe(query)}-article-deep-dive",
            source_code=source_value,
            doc_type="article",
            title=f"{company_name} Valuation Deep Dive",
            company_name=company_name,
            stock_code=query_upper if len(query) <= 5 else None,
            publish_time=now - timedelta(days=1),
            source_name="Alpha Research Mock",
            url=f"https://example.com/articles/{query_lower_safe(query)}-valuation",
            summary=DocumentSummary(
                summary_text="A long-form analysis compares valuation, growth assumptions, and downside risks.",
                key_points=[
                    "Bull case depends on sustained demand growth.",
                    "Base case assumes margin normalization.",
                    "Bear case centers on valuation compression.",
                ],
                tags=["research", "valuation", "deep-dive"],
            ),
            attachments=[],
        ),
    ]


def query_lower_safe(query: str) -> str:
    """Normalize query for safe mock identifiers and URLs."""
    return query.strip().lower().replace(" ", "-")
