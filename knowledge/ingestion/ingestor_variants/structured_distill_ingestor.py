"""StructuredDistillIngestor: uses LLM to produce {when, lesson, scope, evidence}."""

from __future__ import annotations

import json
import re
from typing import Any, Iterable
from uuid import uuid4

from knowledge.ingestion.parent_ingestor import Ingestor, Insight
from knowledge.llm.openrouter import OpenRouterLlm


class StructuredDistillIngestor(Ingestor):
    def __init__(self, llm: OpenRouterLlm | None = None) -> None:
        self.llm = llm or OpenRouterLlm()

    def ingest(self, source: str | Iterable[str], **kwargs: Any) -> list[Insight]:
        texts = [source] if isinstance(source, str) else list(source)
        insights: list[Insight] = []
        for t in texts:
            raw = self.llm.complete(
                "Extract a single learning moment as compact JSON: "
                '{"when":"<when>","lesson":"<lesson>","scope":"<scope>","evidence":"<evidence>"}. '
                f"Input: {t}"
            )
            parsed = self._parse_json(raw) or {}
            insights.append(
                Insight(
                    id=str(uuid4()),
                    title=(parsed.get("lesson") or t)[:60],
                    content=parsed.get("lesson") or raw,
                    provenance=kwargs.get("provenance", "distill"),
                    when=parsed.get("when"),
                    scope=parsed.get("scope"),
                    evidence=parsed.get("evidence") or t[:200],
                )
            )
        return insights

    def _parse_json(self, text: str) -> dict[str, Any] | None:
        try:
            m = re.search(r"\{.*\}", text, re.S)
            if m:
                return json.loads(m.group(0))
        except Exception:
            pass
        return None
