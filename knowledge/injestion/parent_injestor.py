"""Ingestor ABC."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from knowledge.knowledge_graph.abc import Insight


class Ingestor(ABC):
    @abstractmethod
    def ingest(self, source: str | Iterable[str], **kwargs: Any) -> list[Insight]:
        """Ingest raw text/JSONL and return structured Insights with provenance."""
