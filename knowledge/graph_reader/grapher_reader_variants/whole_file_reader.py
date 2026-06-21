"""WholeFileReader: dumps entire active graph for injection (baseline)."""

from __future__ import annotations

from typing import Any

from knowledge.knowledge_graph.abc import Fact, KnowledgeGraph


class WholeFileReader:
    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def read(self, query: str | None = None, limit: int = 50) -> list[Fact]:
        return self.graph.read(query, state="active", limit=limit)

    def as_claude_tool(self) -> dict[str, Any]:
        """Return OpenAI tool schema for Claude tool use."""
        return {
            "name": "praxis_get_context",
            "description": "Retrieve relevant knowledge from the PRAXIS graph.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
        }
