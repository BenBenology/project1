"""Repository for configured crawler sources."""

from __future__ import annotations

from sqlalchemy import select

from backend.app.db.models import SourceModel
from backend.app.db.session import SessionLocal
from backend.app.models.schemas import SourceRecord


DEFAULT_SOURCES = [
    SourceRecord(
        code="official_ir",
        name="Official IR",
        source_type="official",
        base_url="https://example.com/ir",
        crawler_key="mock_financial",
        enabled=1,
        priority=10,
    ),
    SourceRecord(
        code="regulatory_filing",
        name="Regulatory Filing",
        source_type="official",
        base_url="https://example.com/filings",
        crawler_key="mock_financial",
        enabled=1,
        priority=20,
    ),
    SourceRecord(
        code="market_news",
        name="Market News Daily",
        source_type="news",
        base_url="https://example.com/news",
        crawler_key="mock_news",
        enabled=1,
        priority=30,
    ),
]


class SourceRepository:
    """Persist and fetch source definitions."""

    def ensure_default_sources(self) -> None:
        """Seed baseline sources if the table is empty."""
        with SessionLocal.begin() as session:
            existing_codes = set(session.scalars(select(SourceModel.code)).all())
            for source in DEFAULT_SOURCES:
                if source.code in existing_codes:
                    continue
                session.add(
                    SourceModel(
                        code=source.code,
                        name=source.name,
                        source_type=source.source_type,
                        base_url=source.base_url,
                        crawler_key=source.crawler_key,
                        enabled=source.enabled,
                        priority=source.priority,
                    )
                )

    def list_enabled_sources(self) -> list[SourceRecord]:
        """Return enabled sources ordered by priority."""
        with SessionLocal() as session:
            models = session.scalars(
                select(SourceModel)
                .where(SourceModel.enabled == 1)
                .order_by(SourceModel.priority.asc())
            ).all()
            return [SourceRecord.model_validate(model) for model in models]


source_repository = SourceRepository()
