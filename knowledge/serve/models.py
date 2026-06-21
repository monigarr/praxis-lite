"""Pydantic models for candidate-api-v1 (shared with frontend contract tests)."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: str
    title: str
    content: str
    state: Literal["proposed", "suggested", "active", "decayed"] = "proposed"
    confidence: float = 0.5
    provenance: str = ""
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    confidenceBreakdown: dict[str, float] | None = None
    contradictions: list[str] | None = None
    auditTrail: list[dict[str, Any]] | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class PromoteRequest(BaseModel):
    note: str | None = None
