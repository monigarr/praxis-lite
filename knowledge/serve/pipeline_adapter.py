"""Adapter: Candidate <-> Insight/Fact and promote path to graph.write."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from knowledge.knowledge_graph.abc import Fact
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


def apply_promote(store: CandidateStore, graph: Any, cand_id: str, target_state: str | None, actor: str = "dev") -> dict[str, Any] | None:
    cand = store.get(cand_id)
    if not cand:
        return None
    current = cand.get("state", "proposed")
    target = target_state or ("suggested" if current == "proposed" else "active" if current == "suggested" else None)
    if target is None or target not in ("suggested", "active") or current == target:
        return None
    cand["state"] = target
    entry = {"action": "promote", "timestamp": datetime.utcnow().isoformat() + "Z", "actor": actor, "note": f"to {target}"}
    if not cand.get("auditTrail"):
        cand["auditTrail"] = []
    cand["auditTrail"].append(entry)
    if target == "active":
        promote_to_graph(store, graph, cand_id, actor)
    return cand


def apply_reject(store: CandidateStore, cand_id: str, reason: str | None, actor: str = "dev") -> dict[str, Any] | None:
    cand = store.get(cand_id)
    if not cand:
        return None
    cand["state"] = "decayed"
    entry = {"action": "reject", "timestamp": datetime.utcnow().isoformat() + "Z", "actor": actor}
    if reason:
        entry["note"] = reason
    if not cand.get("auditTrail"):
        cand["auditTrail"] = []
    cand["auditTrail"].append(entry)
    store.update_state(cand_id, "decayed")
    return cand


def apply_resolve(store: CandidateStore, cid: str, resolution: str, keep_id: str, actor: str = "dev") -> dict[str, Any] | None:
    if "__" not in cid:
        return None
    primary, rival = cid.split("__", 1)
    loser = rival if keep_id == primary else primary
    kept = store.get(keep_id)
    if not kept:
        return None
    loser_cand = store.get(loser)
    if loser_cand:
        loser_cand["state"] = "decayed"
        if not loser_cand.get("auditTrail"):
            loser_cand["auditTrail"] = []
        loser_cand["auditTrail"].append({"action": "resolve_contradiction_loser", "timestamp": datetime.utcnow().isoformat() + "Z", "actor": actor, "note": f"lost to {keep_id}"})
        store.update_state(loser, "decayed")
    if not kept.get("auditTrail"):
        kept["auditTrail"] = []
    kept["auditTrail"].append({"action": "resolve_contradiction", "timestamp": datetime.utcnow().isoformat() + "Z", "actor": actor, "note": f"{resolution} kept {keep_id}"})
    return kept
