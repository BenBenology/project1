"""Service layer for mock task creation and processing."""

from datetime import UTC, datetime
from time import sleep
from uuid import uuid4

from backend.app.core.config import get_settings
from backend.app.models.schemas import Document, TaskCreateRequest, TaskRecord
from backend.app.repositories.task_repository import task_repository
from backend.app.services.mock_data import build_mock_documents


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
        """Simulate crawl execution and persist mock results."""
        task = task_repository.get_task(task_id)
        if task is None:
            return

        task.status = "running"
        task.progress = 20
        task.started_at = datetime.now(UTC)
        task_repository.save_task(task)

        sleep(self.settings.mock_task_delay_seconds)
        documents = self._generate_documents(task.query)

        task.progress = 100
        task.status = "success"
        task.result_count = len(documents)
        task.finished_at = datetime.now(UTC)
        task_repository.save_documents(task_id, documents)
        task_repository.save_task(task)

    def get_task(self, task_id: str) -> TaskRecord | None:
        """Fetch a task from the repository."""
        return task_repository.get_task(task_id)

    def get_documents(self, task_id: str) -> list[Document]:
        """Fetch generated documents for a task."""
        return list(task_repository.get_documents(task_id))

    def _generate_documents(self, query: str) -> list[Document]:
        """Wrap mock document generation for future crawler replacement."""
        return build_mock_documents(query)


task_service = TaskService()
