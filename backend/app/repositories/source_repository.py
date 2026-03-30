"""Repository for configured crawler sources."""

from __future__ import annotations

from sqlalchemy import select

from backend.app.db.models import SourceModel
from backend.app.db.session import SessionLocal
from backend.app.models.schemas import SourceRecord


DEFAULT_SOURCES = [
    SourceRecord(
        code="company_ir",
        name="Company IR",
        source_type="official",
        base_url="https://ir.tesla.com/",
        crawler_key="company_ir",
        enabled=1,
        priority=5,
    ),
    SourceRecord(
        code="sec_edgar",
        name="SEC EDGAR",
        source_type="official",
        base_url="https://data.sec.gov/submissions/",
        crawler_key="sec_submissions",
        enabled=1,
        priority=10,
    ),
    SourceRecord(
        code="google_news",
        name="Google News",
        source_type="news",
        base_url="https://news.google.com/rss",
        crawler_key="google_news_rss",
        enabled=1,
        priority=20,
    ),
    SourceRecord(
        code="google_news_analyst",
        name="Analyst Coverage",
        source_type="research",
        base_url="https://news.google.com/rss",
        crawler_key="google_news_rss",
        enabled=1,
        priority=30,
    ),
    SourceRecord(
        code="mock_news",
        name="Mock News Fallback",
        source_type="news",
        base_url="https://example.com/news",
        crawler_key="mock_news",
        enabled=0,
        priority=100,
    ),
]


class SourceRepository:
    """Persist and fetch source definitions."""

    def ensure_default_sources(self) -> None:
        """Seed baseline sources if the table is empty."""
        with SessionLocal.begin() as session:
            existing_models = {
                model.code: model for model in session.scalars(select(SourceModel)).all()
            }
            for source in DEFAULT_SOURCES:
                model = existing_models.get(source.code)
                if model is None:
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
                    continue

                model.name = source.name
                model.source_type = source.source_type
                model.base_url = source.base_url
                model.crawler_key = source.crawler_key
                model.enabled = source.enabled
                model.priority = source.priority

            for legacy_code in {"official_ir", "regulatory_filing", "market_news"}:
                model = existing_models.get(legacy_code)
                if model is not None:
                    model.enabled = 0

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
