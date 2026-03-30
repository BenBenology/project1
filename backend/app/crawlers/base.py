"""Crawler interfaces used by the task service."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.app.models.schemas import Document, SourceRecord, TaskRecord


class BaseCrawler(ABC):
    """Abstract crawler contract for one source family."""

    key: str

    @abstractmethod
    def collect(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Collect normalized documents for one task/source pair."""

