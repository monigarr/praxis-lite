"""Eval harness schema (frozen). Defines EvalCase, SeededInsight, DeterministicCheckRef, Rubric."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class DeterministicCheckRef:
    name: str


@dataclass(frozen=True)
class Rubric:
    criteria: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SeededInsight:
    """Knowledge to inject for an eval case.

    via_ingestor: exercises full knowledge pipeline (ingest → graph write)
    direct_to_graph: bypasses ingestor, seeds graph directly (injection-only tests)
    """

    path: Literal["via_ingestor", "direct_to_graph"]
    content: str | None = None  # for direct_to_graph


@dataclass(frozen=True)
class EvalCase:
    """Top-level eval case loaded from cases/<id>/case.yaml."""

    id: str
    description: str
    seed_prompt: str
    seeded_insight: SeededInsight | None = None
    deterministic_checks: list[DeterministicCheckRef] = field(default_factory=list)
    rubric: Rubric | None = None
    expected_outcome: Literal["pass", "fail"] = "pass"
