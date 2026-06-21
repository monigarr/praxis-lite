"""Candidate model and promotion state machine (contract v1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

PromotionState = Literal["proposed", "suggested", "active", "decayed"]


@dataclass
class Candidate:
    """Forward-compatible candidate record.

    Unknown fields from the server are preserved in `extra` so the UI
    never breaks on future contract extensions.
    """

    id: str
    title: str
    content: str
    state: PromotionState | str
    confidence: float
    provenance: str
    created_at: str
    confidence_breakdown: dict[str, float] | None = None
    contradictions: list[str] | None = None
    audit_trail: list[dict[str, Any]] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> Candidate:
        """Parse a server payload into a Candidate.

        Preserves any keys not explicitly modeled in `extra`.
        """
        known = {
            "id",
            "title",
            "content",
            "state",
            "confidence",
            "provenance",
            "createdAt",
            "created_at",
            "confidenceBreakdown",
            "confidence_breakdown",
            "contradictions",
            "auditTrail",
            "audit_trail",
        }
        extra: dict[str, Any] = {k: v for k, v in data.items() if k not in known}

        created_at = data.get("createdAt") or data.get("created_at") or datetime.utcnow().isoformat() + "Z"

        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            state=data["state"],
            confidence=float(data["confidence"]),
            provenance=data["provenance"],
            created_at=created_at,
            confidence_breakdown=data.get("confidenceBreakdown") or data.get("confidence_breakdown"),
            contradictions=data.get("contradictions"),
            audit_trail=data.get("auditTrail") or data.get("audit_trail"),
            extra=extra,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize back to a JSON-safe dict (for API calls)."""
        payload: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "state": self.state,
            "confidence": self.confidence,
            "provenance": self.provenance,
            "createdAt": self.created_at,
        }
        if self.confidence_breakdown:
            payload["confidenceBreakdown"] = self.confidence_breakdown
        if self.contradictions:
            payload["contradictions"] = self.contradictions
        if self.audit_trail:
            payload["auditTrail"] = self.audit_trail
        payload.update(self.extra)
        return payload

    def next_promotion_state(self) -> PromotionState | None:
        """Return the next state in the happy path or None if terminal."""
        if self.state == "proposed":
            return "suggested"
        if self.state == "suggested":
            return "active"
        return None  # active or decayed are terminal for promotion

    def is_low_confidence(self) -> bool:
        return self.confidence < 0.5
