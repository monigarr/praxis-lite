"""In-memory KnowledgeGraph implementation for dev / tests."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from .abc import Fact, Insight, KnowledgeGraph, State


class InMemoryGraph(KnowledgeGraph):
    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}

    def write(self, content: str | Insight | Fact, /, **kwargs: Any) -> str:
        if isinstance(content, Fact):
            fact = content
        elif isinstance(content, Insight):
            fact = Fact(
                id=content.id or str(uuid4()),
                title=content.title,
                content=content.content,
                provenance=content.provenance,
                confidence=content.confidence,
                created_at=content.created_at,
                extra=content.extra,
            )
        else:
            # raw string passthrough (legacy path)
            fact = Fact(
                id=str(uuid4()),
                title=content[:80],
                content=content,
                provenance=kwargs.get("provenance", "unknown"),
            )
        self._facts[fact.id] = fact
        return fact.id

    def read(self, query: str | None = None, *, state: State | None = None, limit: int = 100) -> list[Fact]:
        facts = list(self._facts.values())
        if state:
            facts = [f for f in facts if f.state == state]
        if query:
            q = query.lower()
            facts = [f for f in facts if q in f.content.lower() or q in f.title.lower()]
        return facts[:limit]

    def update_state(self, fact_id: str, new_state: State) -> None:
        if fact_id in self._facts:
            self._facts[fact_id].state = new_state
            self._facts[fact_id].updated_at = datetime.utcnow()

    def list_contradictions(self, fact_id: str) -> list[Fact]:
        fact = self._facts.get(fact_id)
        if not fact:
            return []
        return [self._facts[cid] for cid in fact.contradictions if cid in self._facts]
