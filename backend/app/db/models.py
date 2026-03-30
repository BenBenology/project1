"""ORM models backing the formal backend persistence layer."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


def utcnow() -> datetime:
    """Return a UTC timestamp for default ORM fields."""
    return datetime.now(UTC)


class TaskModel(Base):
    """Persisted crawl/search task."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    query: Mapped[str] = mapped_column(String(255), index=True)
    query_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    documents: Mapped[list["DocumentModel"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    source_runs: Mapped[list["TaskSourceRunModel"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )


class SourceModel(Base):
    """Persisted source definition for crawler selection."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    base_url: Mapped[str] = mapped_column(String(255))
    crawler_key: Mapped[str] = mapped_column(String(64))
    enabled: Mapped[int] = mapped_column(Integer, default=1)
    priority: Mapped[int] = mapped_column(Integer, default=100)


class DocumentModel(Base):
    """Persisted normalized document."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True)
    source_code: Mapped[str] = mapped_column(String(64), index=True)
    doc_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(500))
    company_name: Mapped[str] = mapped_column(String(255))
    stock_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    publish_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(Text)
    summary_text: Mapped[str] = mapped_column(Text)
    key_points_json: Mapped[str] = mapped_column(Text)
    tags_json: Mapped[str] = mapped_column(Text)

    task: Mapped[TaskModel] = relationship(back_populates="documents")
    attachments: Mapped[list["AttachmentModel"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class AttachmentModel(Base):
    """Persisted document attachment."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    file_type: Mapped[str] = mapped_column(String(32))
    file_name: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(Text)

    document: Mapped[DocumentModel] = relationship(back_populates="attachments")


class TaskSourceRunModel(Base):
    """Persisted per-source execution results for one task."""

    __tablename__ = "task_source_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True)
    source_code: Mapped[str] = mapped_column(String(64), index=True)
    source_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32), index=True)
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped[TaskModel] = relationship(back_populates="source_runs")
