"""StructuredDistillIngestor: uses LLM to produce {when, lesson, scope, evidence}."""

from __future__ import annotations

from typing import Any, Iterable
from uuid import uuid4

from knowledge.injestion.parent_injestor import Ingestor, Insight
from knowledge.llm.openrouter import OpenRouterLlm


class StructuredDistillIngestor(Ingestor):
    def __init__(self, llm: OpenRouterLlm | None = None) -> None:
        self.llm = llm or OpenRouterLlm()

    def ingest(self, source: str | Iterable[str], **kwargs: Any) -> list[Insight]:
        texts = [source] if isinstance(source, str) else list(source)
        insights: list[Insight] = []
        for t in texts:
            # Prompt stub — real impl would parse JSON from LLM
            distilled = self.llm.complete(f"Distill lesson: {t}\nReturn JSON with when,lesson,scope,evidence.")
            insights.append(
                Insight(
                    id=str(uuid4()),
                    title=distilled[:60],
                    content=distilled,
                    provenance=kwargs.get("provenance", "distill"),
                    when="recent",
                    scope="general",
                    evidence=t[:200],
                )
            )
        return insights
