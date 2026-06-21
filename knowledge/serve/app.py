"""FastAPI app implementing candidate-api-v1 contract.

Supports PRAXIS_AUTH_DISABLED=1 dev mode and Cognito JWT (stubbed).
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from knowledge.knowledge_graph import InMemoryGraph
from knowledge.serve.auth import get_current_user, require_org
from knowledge.serve.candidate_store import CandidateStore
from knowledge.serve.pipeline_adapter import to_candidate, promote_to_graph

app = FastAPI(title="PRAXIS Candidate API", version="1.0.0")

# Global stores (JSON mode default; swap to Postgres via PRAXIS_DB_URL)
_graph = InMemoryGraph()
_store = CandidateStore(_graph)


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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "contract": "1"}


@app.get("/candidates", response_model=list[Candidate] | dict[str, list[Candidate]])
def list_candidates(
    state: Literal["proposed", "suggested", "active", "decayed"] | None = Query(None),
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
) -> Any:
    require_org(current_user, org)
    cands = _store.list(state=state)
    return {"candidates": [to_candidate(c) for c in cands]}


@app.get("/candidates/{cand_id}", response_model=Candidate)
def get_candidate(
    cand_id: str,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
) -> Candidate:
    require_org(current_user, org)
    cand = _store.get(cand_id)
    if not cand:
        raise HTTPException(404, "Candidate not found")
    return to_candidate(cand)


@app.post("/candidates/{cand_id}/promote")
def promote(
    cand_id: str,
    body: PromoteRequest | None = None,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
) -> dict[str, str]:
    require_org(current_user, org)
    fact_id = promote_to_graph(_store, _graph, cand_id, actor=current_user.get("sub", "dev"))
    return {"status": "promoted", "fact_id": fact_id}


# Additional stubs for reject/resolve/ingest to satisfy contract surface
@app.post("/candidates/{cand_id}/reject")
def reject(cand_id: str, current_user=Depends(get_current_user), org: str = Header("default", alias="X-Praxis-Org")) -> dict[str, str]:
    require_org(current_user, org)
    _store.update_state(cand_id, "decayed")
    return {"status": "rejected"}


@app.post("/ingest/jsonl")
def ingest_jsonl(payload: dict[str, Any], current_user=Depends(get_current_user), org: str = Header("default", alias="X-Praxis-Org")) -> dict[str, Any]:
    require_org(current_user, org)
    # TODO: wire real JsonlIngestor + distill
    return {"status": "accepted", "count": 0}


# ---------------- Eval metrics endpoint (placeholder) ----------------
from pathlib import Path
import json

_EVAL_RESULTS = Path(__file__).parent.parent / "evals" / "results" / "baseline.jsonl"


@app.get("/metrics")
def eval_metrics() -> dict[str, Any]:
    """Return eval-metrics-v1 contract shape derived from baseline.jsonl.

    Falls back to fixture-like empty shape when no runs exist.
    """
    correction_rate: list[float] = []
    sessions: list[str] = []
    corrections_before = 0
    corrections_after = 0

    if _EVAL_RESULTS.exists():
        runs = [json.loads(line) for line in _EVAL_RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]
        # Aggregate by mode order (cold first, then injected runs)
        by_mode: dict[str, list[dict[str, Any]]] = {}
        for r in runs:
            by_mode.setdefault(r["mode"], []).append(r)
        # Simple curve: cold baseline then successive injected runs
        if "cold" in by_mode:
            cold = by_mode["cold"][0]
            corrections_before = cold.get("correction_count", 0)
            correction_rate.append(cold.get("correction_count", 0))
            sessions.append("cold")
        if "injected" in by_mode:
            for i, r in enumerate(by_mode["injected"]):
                corrections_after = r.get("correction_count", 0)
                correction_rate.append(corrections_after)
                sessions.append(f"run_{i+1}")

    return {
        "correction_rate": correction_rate or [0.0],
        "sessions": sessions or ["cold"],
        "corrections_before": corrections_before,
        "corrections_after": corrections_after,
    }
