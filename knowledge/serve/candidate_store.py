"""CandidateStore backed by KnowledgeGraph (proposed/suggested only until promote)."""

from __future__ import annotations

import os
from typing import Any

from knowledge.knowledge_graph.abc import KnowledgeGraph, State


class CandidateStore:
    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph
        self._candidates: dict[str, dict[str, Any]] = {}
        self._use_postgres = bool(os.getenv("PRAXIS_DB_URL"))

    def create(self, data: dict[str, Any]) -> str:
        cid = data.get("id") or str(__import__("uuid").uuid4())
        self._candidates[cid] = data
        return cid

    def list(self, state: State | None = None) -> list[dict[str, Any]]:
        vals = list(self._candidates.values())
        if state:
            vals = [v for v in vals if v.get("state") == state]
        return vals

    def get(self, cid: str) -> dict[str, Any] | None:
        return self._candidates.get(cid)

    def update_state(self, cid: str, new_state: State) -> None:
        if cid in self._candidates:
            self._candidates[cid]["state"] = new_state
        self.graph.update_state(cid, new_state)
