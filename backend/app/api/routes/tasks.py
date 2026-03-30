"""Task-related endpoints for the mock crawl flow."""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.app.models.schemas import (
    DocumentListResponse,
    SourceRunListResponse,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskDetailResponse,
)
from backend.app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskCreateResponse)
def create_task(
    payload: TaskCreateRequest, background_tasks: BackgroundTasks
) -> TaskCreateResponse:
    """Create a task and process it asynchronously."""
    task = task_service.create_task(payload)
    background_tasks.add_task(task_service.process_task, task.id)
    return TaskCreateResponse(
        task_id=task.id,
        status=task.status,
        message="Task created.",
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str) -> TaskDetailResponse:
    """Return the task progress and summary."""
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return TaskDetailResponse.model_validate(task)


@router.get("/{task_id}/documents", response_model=DocumentListResponse)
def get_task_documents(task_id: str) -> DocumentListResponse:
    """Return documents generated for a specific task."""
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    documents = task_service.get_documents(task_id)
    return DocumentListResponse(task_id=task_id, count=len(documents), items=documents)


@router.get("/{task_id}/sources", response_model=SourceRunListResponse)
def get_task_sources(task_id: str) -> SourceRunListResponse:
    """Return per-source execution results for a task."""
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    source_runs = task_service.get_source_runs(task_id)
    return SourceRunListResponse(task_id=task_id, count=len(source_runs), items=source_runs)
