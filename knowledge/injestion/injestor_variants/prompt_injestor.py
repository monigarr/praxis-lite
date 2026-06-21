"""Simple passthrough / LLM-prompt ingestor."""

from __future__ import annotations

from typing import Any, Iterable
from uuid import uuid4

from knowledge.injestion.parent_injestor import Ingestor, Insight


class PromptIngestor(Ingestor):
    def ingest(self, source: str | Iterable[str], **kwargs: Any) -> list[Insight]:
        texts = [source] if isinstance(source, str) else list(source)
        return [
            Insight(
                id=str(uuid4()),
                title=t[:60],
                content=t,
                provenance=kwargs.get("provenance", "prompt"),
            )
            for t in texts
        ]
