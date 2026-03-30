"""Service layer for mock task creation and processing."""

from collections import OrderedDict
from datetime import UTC, datetime
from time import sleep
from uuid import uuid4

from backend.app.crawlers.registry import crawler_registry
from backend.app.core.config import get_settings
from backend.app.models.schemas import Document, TaskCreateRequest, TaskRecord
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
        documents, source_errors = self._generate_documents(task)

        task.progress = 100
        task.result_count = len(documents)
        task.finished_at = datetime.now(UTC)
        if documents and source_errors:
            task.status = "partial_success"
            task.error_message = " | ".join(source_errors)
        elif documents:
            task.status = "success"
            task.error_message = None
        else:
            task.status = "failed"
            task.error_message = " | ".join(source_errors) or "No documents found for query."
        task_repository.save_documents(task_id, documents)
        task_repository.save_task(task)

    def get_task(self, task_id: str) -> TaskRecord | None:
        """Fetch a task from the repository."""
        return task_repository.get_task(task_id)

    def get_documents(self, task_id: str) -> list[Document]:
        """Fetch generated documents for a task."""
        return list(task_repository.get_documents(task_id))

    def _generate_documents(self, task: TaskRecord) -> tuple[list[Document], list[str]]:
        """Collect documents from enabled sources through the crawler registry."""
        source_repository.ensure_default_sources()
        documents_by_id: OrderedDict[str, Document] = OrderedDict()
        source_errors: list[str] = []

        for source in source_repository.list_enabled_sources():
            try:
                crawler = crawler_registry.get(source.crawler_key)
                for document in crawler.collect(task, source):
                    dedupe_key = f"{document.source_code}:{document.title}:{document.url}"
                    documents_by_id.setdefault(dedupe_key, document)
            except Exception as exc:
                source_errors.append(f"{source.name}: {exc}")

        return list(documents_by_id.values()), source_errors


task_service = TaskService()
