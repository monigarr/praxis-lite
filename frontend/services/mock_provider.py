"""In-memory mock provider for offline demo and contract tests."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from ..models.candidate import Candidate, PromotionState
from .data_provider import DataProvider


class MockDataProvider(DataProvider):
    """Fully functional in-memory implementation.

    Used when PRAXIS_API_BASE_URL is unset. Supports the full promote/reject/resolve
    lifecycle and maintains an audit trail on each mutation.
    """

    def __init__(self, seed: list[dict[str, Any]] | None = None) -> None:
        from ..mock_data import SEED_CANDIDATES

        raw = seed or SEED_CANDIDATES
        self._store: dict[str, Candidate] = {c.id: deepcopy(c) for c in raw}
        self._contradiction_pairs: set[tuple[str, str]] = set()

    # ------------------------------------------------------------------ queries
    def list_candidates(self, state: PromotionState | None = None) -> list[Candidate]:
        if state is None:
            return list(self._store.values())
        return [c for c in self._store.values() if c.state == state]

    def get_candidate(self, candidate_id: str) -> Candidate | None:
        return self._store.get(candidate_id)

    # ------------------------------------------------------------------ mutations
    def promote(self, candidate_id: str, target_state: PromotionState | None = None) -> Candidate:
        cand = self._require(candidate_id)
        next_state = target_state or cand.next_promotion_state()
        if next_state is None:
            raise ValueError(f"Cannot promote terminal state {cand.state}")
        self._append_audit(cand, "promote", note=f"to {next_state}")
        cand.state = next_state
        return cand

    def reject(self, candidate_id: str, reason: str | None = None) -> Candidate:
        cand = self._require(candidate_id)
        self._append_audit(cand, "reject", note=reason)
        cand.state = "decayed"
        return cand

    def resolve_contradiction(
        self, primary_id: str, rival_id: str, resolution: str, keep_id: str
    ) -> Candidate:
        kept = self._require(keep_id)
        self._append_audit(
            kept,
            "resolve_contradiction",
            note=f"{resolution} (kept {keep_id}) vs {primary_id}/{rival_id}",
        )
        # Mark the loser as decayed for demo purposes
        loser_id = primary_id if keep_id == rival_id else rival_id
        if loser_id in self._store:
            loser = self._store[loser_id]
            loser.state = "decayed"
            self._append_audit(loser, "resolve_contradiction_loser", note=f"lost to {keep_id}")
        self._contradiction_pairs.add(tuple(sorted([primary_id, rival_id])))
        return kept

    # ------------------------------------------------------------------ helpers
    def _require(self, candidate_id: str) -> Candidate:
        if candidate_id not in self._store:
            raise KeyError(candidate_id)
        return self._store[candidate_id]

    def _append_audit(self, cand: Candidate, action: str, note: str | None = None) -> None:
        entry: dict[str, Any] = {
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provenance": "mock_provider",
            "actor": "human",
        }
        if note:
            entry["note"] = note
        if cand.audit_trail is None:
            cand.audit_trail = []
        cand.audit_trail.append(entry)
