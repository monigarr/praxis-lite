"""RetrievingReader: BM25 + dense + RRF retrieval with confidence / state filter."""

from __future__ import annotations

from typing import Any

import numpy as np

from knowledge.knowledge_graph.abc import Fact, KnowledgeGraph
from knowledge.llm.openrouter import OpenRouterEmbedder


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in text.split() if t.isalnum()]


class RetrievingReader:
    def __init__(self, graph: KnowledgeGraph, min_confidence: float = 0.4, embedder: OpenRouterEmbedder | None = None) -> None:
        self.graph = graph
        self.min_confidence = min_confidence
        self.embedder = embedder or OpenRouterEmbedder()

    def read(self, query: str | None = None, limit: int = 20) -> list[Fact]:
        all_facts = self.graph.read(query, state="active", limit=200)
        filtered = [f for f in all_facts if f.confidence >= self.min_confidence]
        if not query or not filtered:
            return filtered[:limit]
        q_tokens = _tokenize(query)
        q_vec = np.array(self.embedder.embed(query), dtype=np.float32)
        scored: list[tuple[Fact, float]] = []
        for f in filtered:
            f_tokens = _tokenize(f.content)
            overlap = len(set(q_tokens) & set(f_tokens))
            bm25 = overlap / (len(q_tokens) + 1)
            f_vec = np.array(self.embedder.embed(f.content), dtype=np.float32)
            dense = float(np.dot(q_vec, f_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(f_vec) + 1e-9))
            rrf = 1.0 / (60 + bm25) + 1.0 / (60 + dense)
            scored.append((f, rrf))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [f for f, _ in scored[:limit]]

    def as_claude_tool(self) -> dict[str, Any]:
        return {
            "name": "praxis_get_context",
            "description": "Retrieve ranked knowledge from PRAXIS graph (promoted facts only).",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
        }
