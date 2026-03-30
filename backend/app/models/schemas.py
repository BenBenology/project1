"""Pydantic schemas for requests and responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

QueryType = Literal["company", "stock", "industry", "topic"]
TaskStatus = Literal["pending", "running", "success", "partial_success", "failed"]
DocumentType = Literal["report", "filing", "news", "article"]


class TaskCreateRequest(BaseModel):
    """Input payload for creating a crawl task."""

    query: str = Field(..., min_length=1, max_length=255)
    query_type: QueryType = "company"


class TaskCreateResponse(BaseModel):
    """Response returned after task creation."""

    task_id: str
    status: TaskStatus
    message: str


class DocumentAttachment(BaseModel):
    """Normalized attachment metadata for the UI."""

    file_type: str
    file_name: str
    file_url: str


class DocumentSummary(BaseModel):
    """Summary block prepared for future AI integration."""

    summary_text: str
    key_points: list[str]
    tags: list[str]


class Document(BaseModel):
    """Single normalized document item."""

    id: str
    source_code: str | None = None
    doc_type: DocumentType
    title: str
    company_name: str
    stock_code: str | None = None
    publish_time: datetime
    source_name: str
    url: str
    summary: DocumentSummary
    attachments: list[DocumentAttachment] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    """List response for task documents."""

    task_id: str
    count: int
    items: list[Document]


class SourceRunRecord(BaseModel):
    """Per-source execution result for a task."""

    model_config = ConfigDict(from_attributes=True)

    source_code: str
    source_name: str
    status: str
    document_count: int
    error_message: str | None = None


class SourceRunListResponse(BaseModel):
    """List response for source execution details."""

    task_id: str
    count: int
    items: list[SourceRunRecord]


class TaskRecord(BaseModel):
    """Internal and API-safe representation of a task."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    query: str
    query_type: QueryType
    status: TaskStatus
    progress: int
    result_count: int = 0
    error_message: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class TaskDetailResponse(TaskRecord):
    """Task detail response returned to clients."""

    pass


class SourceRecord(BaseModel):
    """Persisted source definition used by crawler dispatch."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    code: str
    name: str
    source_type: str
    base_url: str
    crawler_key: str
    enabled: int = 1
    priority: int = 100
