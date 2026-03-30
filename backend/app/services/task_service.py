"""Service layer for mock task creation and processing."""

from collections import OrderedDict
from datetime import UTC, datetime
from time import sleep
from uuid import uuid4

from backend.app.crawlers.registry import crawler_registry
from backend.app.core.config import get_settings
from backend.app.models.schemas import Document, SourceRunRecord, TaskCreateRequest, TaskRecord
from backend.app.repositories.source_repository import source_repository
from backend.app.repositories.task_repository import task_repository


class TaskService:
    """Coordinate task lifecycle and mock document generation."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def create_task(self, payload: TaskCreateRequest) -> TaskRecord:
        """Create a pending task before background execution starts."""
        now = datetime.now(UTC)
        task = TaskRecord(
            id=str(uuid4()),
            query=payload.query.strip(),
            query_type=payload.query_type,
            status="pending",
            progress=0,
            created_at=now,
            started_at=None,
            finished_at=None,
        )
        return task_repository.save_task(task)

    def process_task(self, task_id: str) -> None:
        """Run a task through the configured crawler sources."""
        task = task_repository.get_task(task_id)
        if task is None:
            return

        task.status = "running"
        task.progress = 20
        task.started_at = datetime.now(UTC)
        task_repository.save_task(task)

        sleep(self.settings.mock_task_delay_seconds)
        documents, source_runs = self._generate_documents(task)

        task.progress = 100
        task.result_count = len(documents)
        task.finished_at = datetime.now(UTC)
        failed_source_messages = [
            f"{run.source_name}: {run.error_message}"
            for run in source_runs
            if run.status == "failed" and run.error_message
        ]
        if documents and failed_source_messages:
            task.status = "partial_success"
            task.error_message = " | ".join(failed_source_messages)
        elif documents:
            task.status = "success"
            task.error_message = None
        else:
            task.status = "failed"
            task.error_message = " | ".join(failed_source_messages) or "No documents found for query."
        task_repository.save_documents(task_id, documents)
        task_repository.save_source_runs(task_id, source_runs)
        task_repository.save_task(task)

    def get_task(self, task_id: str) -> TaskRecord | None:
        """Fetch a task from the repository."""
        return task_repository.get_task(task_id)

    def get_documents(self, task_id: str) -> list[Document]:
        """Fetch generated documents for a task."""
        return list(task_repository.get_documents(task_id))

    def get_source_runs(self, task_id: str) -> list[SourceRunRecord]:
        """Fetch source-level execution results for a task."""
        return list(task_repository.get_source_runs(task_id))

    def _generate_documents(self, task: TaskRecord) -> tuple[list[Document], list[SourceRunRecord]]:
        """Collect documents from enabled sources through the crawler registry."""
        source_repository.ensure_default_sources()
        documents_by_id: OrderedDict[str, Document] = OrderedDict()
        source_runs: list[SourceRunRecord] = []

        for source in source_repository.list_enabled_sources():
            try:
                crawler = crawler_registry.get(source.crawler_key)
                source_documents = crawler.collect(task, source)
                added_count = 0
                for document in source_documents:
                    dedupe_key = f"{document.source_code}:{document.title}:{document.url}"
                    if dedupe_key not in documents_by_id:
                        documents_by_id[dedupe_key] = document
                        added_count += 1
                source_runs.append(
                    SourceRunRecord(
                        source_code=source.code,
                        source_name=source.name,
                        status="success",
                        document_count=added_count,
                        error_message=None,
                    )
                )
            except Exception as exc:
                source_runs.append(
                    SourceRunRecord(
                        source_code=source.code,
                        source_name=source.name,
                        status="failed",
                        document_count=0,
                        error_message=str(exc),
                    )
                )

        return list(documents_by_id.values()), source_runs


task_service = TaskService()
