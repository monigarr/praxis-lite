"""KnowledgeGraph abstract base and core data models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, Literal, Optional


State = Literal["proposed", "suggested", "active", "decayed"]


@dataclass
class Insight:
    """Raw learning moment distilled from logs before consolidation."""

    id: str
    title: str
    content: str
    provenance: str  # e.g. "logs/session_20260615.jsonl:88"
    when: Optional[str] = None
    scope: Optional[str] = None
    evidence: Optional[str] = None
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Fact:
    """Consolidated, scored, stateful knowledge unit persisted in the graph."""

    id: str
    title: str
    content: str
    state: State = "proposed"
    confidence: float = 0.5
    provenance: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    confidence_breakdown: dict[str, float] = field(default_factory=dict)
    contradictions: list[str] = field(default_factory=list)
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph(ABC):
    """Abstract base for all knowledge stores (in-memory, pgvector, etc.)."""

    @abstractmethod
    def write(self, content: str | Insight | Fact, /, **kwargs: Any) -> str:
        """Write raw text, Insight, or Fact. Returns the fact id."""

    @abstractmethod
    def read(self, query: str | None = None, *, state: State | None = None, limit: int = 100) -> list[Fact]:
        """Retrieve facts, optionally filtered."""

    @abstractmethod
    def update_state(self, fact_id: str, new_state: State) -> None:
        """Promote / reject / decay a fact."""

    @abstractmethod
    def list_contradictions(self, fact_id: str) -> list[Fact]:
        """Return known contradictory facts for a given fact."""

    def close(self) -> None:
        """Optional cleanup (e.g. DB connections)."""
        pass
