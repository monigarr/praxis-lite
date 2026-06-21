"""Adapter: Candidate <-> Insight/Fact and promote path to graph.write."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from knowledge.knowledge_graph.abc import Fact, Insight
from knowledge.serve.candidate_store import CandidateStore


def to_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "title": raw.get("title", ""),
        "content": raw.get("content", ""),
        "state": raw.get("state", "proposed"),
        "confidence": raw.get("confidence", 0.5),
        "provenance": raw.get("provenance", ""),
        "createdAt": raw.get("createdAt") or datetime.utcnow().isoformat() + "Z",
        "confidenceBreakdown": raw.get("confidenceBreakdown"),
        "contradictions": raw.get("contradictions"),
        "auditTrail": raw.get("auditTrail"),
        "extra": raw.get("extra", {}),
    }


def promote_to_graph(store: CandidateStore, graph: Any, cand_id: str, actor: str = "dev") -> str:
    cand = store.get(cand_id)
    if not cand:
        return ""
    fact = Fact(
        id=cand_id,
        title=cand["title"],
        content=cand["content"],
        state="active",
        confidence=cand.get("confidence", 0.5),
        provenance=cand.get("provenance", ""),
        audit_trail=[{"action": "promote", "timestamp": datetime.utcnow().isoformat(), "actor": actor}],
    )
    return graph.write(fact)
