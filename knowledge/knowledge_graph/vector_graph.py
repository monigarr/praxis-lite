"""VectorGraph: in-memory vector store with optional embedding."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import numpy as np

from knowledge.llm.openrouter import OpenRouterEmbedder

from .abc import Fact, Insight, KnowledgeGraph, State


class VectorGraph(KnowledgeGraph):
    """In-memory vector store. Embeds on write if embedder available."""

    def __init__(self, dsn: str | None = None, embedder: OpenRouterEmbedder | None = None) -> None:
        self.dsn = dsn
        self.embedder = embedder or OpenRouterEmbedder()
        self._facts: dict[str, Fact] = {}
        self._vecs: dict[str, np.ndarray] = {}

    def _embed(self, text: str) -> np.ndarray:
        v = np.array(self.embedder.embed(text), dtype=np.float32)
        if v.sum() == 0:
            v = np.random.default_rng(42).standard_normal(1536).astype(np.float32)
        return v

    def write(self, content: str | Insight | Fact, /, **kwargs: Any) -> str:
        if isinstance(content, Fact):
            fact = content
        elif isinstance(content, Insight):
            fact = Fact(id=content.id or str(uuid4()), title=content.title, content=content.content, provenance=content.provenance, confidence=content.confidence)
        else:
            fact = Fact(id=str(uuid4()), title=content[:80], content=content, provenance=kwargs.get("provenance", ""))
        self._facts[fact.id] = fact
        self._vecs[fact.id] = self._embed(fact.content)
        return fact.id

    def read(self, query: str | None = None, *, state: State | None = None, limit: int = 100) -> list[Fact]:
        facts = list(self._facts.values())
        if state:
            facts = [f for f in facts if f.state == state]
        if query:
            qv = self._embed(query)
            scored = [(f, float(np.dot(self._vecs.get(f.id, np.zeros(1536)), qv))) for f in facts]
            scored.sort(key=lambda x: x[1], reverse=True)
            facts = [f for f, _ in scored]
        return facts[:limit]

    def update_state(self, fact_id: str, new_state: State) -> None:
        if fact_id in self._facts:
            self._facts[fact_id].state = new_state

    def list_contradictions(self, fact_id: str) -> list[Fact]:
        return []
