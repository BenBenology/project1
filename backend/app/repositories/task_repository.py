"""SQLAlchemy-backed repository for tasks and documents."""

from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select

from backend.app.db.models import AttachmentModel, DocumentModel, TaskModel
from backend.app.db.session import SessionLocal
from backend.app.models.schemas import Document, DocumentAttachment, DocumentSummary, TaskRecord


class SqlAlchemyTaskRepository:
    """Persist tasks and normalized documents in the database."""

    def save_task(self, task: TaskRecord) -> TaskRecord:
        """Insert or update a task."""
        with SessionLocal.begin() as session:
            model = session.get(TaskModel, task.id)
            if model is None:
                model = TaskModel(id=task.id)
                session.add(model)

            model.query = task.query
            model.query_type = task.query_type
            model.status = task.status
            model.progress = task.progress
            model.result_count = task.result_count
            model.error_message = task.error_message
            model.created_at = task.created_at
            model.started_at = task.started_at
            model.finished_at = task.finished_at

        return task

    def get_task(self, task_id: str) -> TaskRecord | None:
        """Fetch a task by its id."""
        with SessionLocal() as session:
            model = session.get(TaskModel, task_id)
            if model is None:
                return None
            return TaskRecord.model_validate(model)

    def save_documents(self, task_id: str, documents: list[Document]) -> None:
        """Replace the documents for a task with a fresh normalized set."""
        with SessionLocal.begin() as session:
            task = session.get(TaskModel, task_id)
            if task is None:
                return

            existing_docs = session.scalars(
                select(DocumentModel).where(DocumentModel.task_id == task_id)
            ).all()
            for existing_doc in existing_docs:
                session.delete(existing_doc)

            for document in documents:
                persisted_id = f"{task_id}:{document.id}"
                model = DocumentModel(
                    id=persisted_id,
                    task_id=task_id,
                    source_code=document.source_code or "unknown",
                    doc_type=document.doc_type,
                    title=document.title,
                    company_name=document.company_name,
                    stock_code=document.stock_code,
                    publish_time=document.publish_time,
                    source_name=document.source_name,
                    url=document.url,
                    summary_text=document.summary.summary_text,
                    key_points_json=json.dumps(document.summary.key_points),
                    tags_json=json.dumps(document.summary.tags),
                )
                session.add(model)
                for attachment in document.attachments:
                    session.add(
                        AttachmentModel(
                            document=model,
                            file_type=attachment.file_type,
                            file_name=attachment.file_name,
                            file_url=attachment.file_url,
                        )
                    )

    def get_documents(self, task_id: str) -> Sequence[Document]:
        """Fetch normalized documents for a task."""
        with SessionLocal() as session:
            models = session.scalars(
                select(DocumentModel)
                .where(DocumentModel.task_id == task_id)
                .order_by(DocumentModel.publish_time.desc())
            ).all()
            return [self._to_document(model) for model in models]

    def _to_document(self, model: DocumentModel) -> Document:
        """Convert an ORM model into the API-safe schema."""
        return Document(
            id=model.id,
            source_code=model.source_code,
            doc_type=model.doc_type,
            title=model.title,
            company_name=model.company_name,
            stock_code=model.stock_code,
            publish_time=model.publish_time,
            source_name=model.source_name,
            url=model.url,
            summary=DocumentSummary(
                summary_text=model.summary_text,
                key_points=json.loads(model.key_points_json),
                tags=json.loads(model.tags_json),
            ),
            attachments=[
                DocumentAttachment(
                    file_type=attachment.file_type,
                    file_name=attachment.file_name,
                    file_url=attachment.file_url,
                )
                for attachment in model.attachments
            ],
        )


task_repository = SqlAlchemyTaskRepository()
