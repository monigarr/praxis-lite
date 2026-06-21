"""VectorGraph (pgvector) implementation skeleton. Full RDS wiring in serve/postgres_store."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from .abc import Fact, Insight, KnowledgeGraph, State


class VectorGraph(KnowledgeGraph):
    """Stub for pgvector-backed store. Real implementation uses PostgresVectorGraph in serve/."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn
        self._facts: dict[str, Fact] = {}  # fallback in-memory for now

    def write(self, content: str | Insight | Fact, /, **kwargs: Any) -> str:
        # TODO: embed + INSERT into facts table with vector
        if isinstance(content, Fact):
            fact = content
        elif isinstance(content, Insight):
            fact = Fact(id=content.id or str(uuid4()), title=content.title, content=content.content, provenance=content.provenance, confidence=content.confidence)
        else:
            fact = Fact(id=str(uuid4()), title=content[:80], content=content, provenance=kwargs.get("provenance", ""))
        self._facts[fact.id] = fact
        return fact.id

    def read(self, query: str | None = None, *, state: State | None = None, limit: int = 100) -> list[Fact]:
        facts = list(self._facts.values())
        if state:
            facts = [f for f in facts if f.state == state]
        return facts[:limit]

    def update_state(self, fact_id: str, new_state: State) -> None:
        if fact_id in self._facts:
            self._facts[fact_id].state = new_state

    def list_contradictions(self, fact_id: str) -> list[Fact]:
        return []
