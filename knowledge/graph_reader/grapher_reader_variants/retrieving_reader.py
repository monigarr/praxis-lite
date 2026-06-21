"""RetrievingReader: BM25 + dense + RRF retrieval with confidence / state filter."""

from __future__ import annotations

from typing import Any

from knowledge.knowledge_graph.abc import Fact, KnowledgeGraph


class RetrievingReader:
    def __init__(self, graph: KnowledgeGraph, min_confidence: float = 0.4) -> None:
        self.graph = graph
        self.min_confidence = min_confidence

    def read(self, query: str | None = None, limit: int = 20) -> list[Fact]:
        # Filter to active + confidence
        all_facts = self.graph.read(query, state="active", limit=200)
        filtered = [f for f in all_facts if f.confidence >= self.min_confidence]
        # TODO: real BM25 + embedding RRF rerank
        return filtered[:limit]

    def as_claude_tool(self) -> dict[str, Any]:
        return {
            "name": "praxis_get_context",
            "description": "Retrieve ranked knowledge from PRAXIS graph (promoted facts only).",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
        }
