"""JsonlIngestor: parses session JSONL lines into Insights with line-level provenance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from knowledge.injestion.parent_injestor import Ingestor, Insight


class JsonlIngestor(Ingestor):
    def ingest(self, source: str | Iterable[str], **kwargs: Any) -> list[Insight]:
        path = Path(source) if isinstance(source, str) else None
        lines: list[str] = []
        if path and path.exists():
            lines = path.read_text(encoding="utf-8").splitlines()
        elif isinstance(source, str):
            lines = source.splitlines()
        else:
            lines = list(source)
        insights: list[Insight] = []
        for idx, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
            except Exception:
                continue
            text = obj.get("text") or obj.get("content") or str(obj)
            insights.append(
                Insight(
                    id=str(uuid4()),
                    title=text[:60],
                    content=text,
                    provenance=f"{path or 'jsonl'}:{idx}",
                    when=obj.get("timestamp"),
                    scope=obj.get("scope"),
                )
            )
        return insights
