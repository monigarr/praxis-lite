"""FastAPI app implementing candidate-api-v1 contract.

Supports PRAXIS_AUTH_DISABLED=1 dev mode and Cognito JWT (stubbed).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from knowledge.knowledge_graph import InMemoryGraph
from knowledge.serve.auth import get_current_user, require_org
from knowledge.serve.candidate_store import CandidateStore
from knowledge.serve.pipeline_adapter import apply_promote, apply_reject, apply_resolve, to_candidate

app = FastAPI(title="PRAXIS Candidate API", version="1.0.0")


def require_contract(contract: str = Header(None, alias="X-Praxis-Contract")) -> None:
    if contract != "1":
        raise HTTPException(400, "Missing or invalid X-Praxis-Contract header")

# Global stores (JSON mode default; swap to Postgres via PRAXIS_DB_URL)
if os.getenv("PRAXIS_DB_URL"):
    from knowledge.serve.postgres_store import PostgresVectorGraph
    _graph: Any = PostgresVectorGraph()
else:
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
    targetState: Literal["proposed", "suggested", "active", "decayed"] | None = None


class RejectRequest(BaseModel):
    reason: str | None = None


class ResolveRequest(BaseModel):
    resolution: Literal["keep_a", "keep_b"]
    keepId: str


class IngestRequest(BaseModel):
    files: list[dict[str, Any]] = Field(default_factory=list)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "contract": "1"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "contract": "1"}


@app.get("/candidates", response_model=list[Candidate] | dict[str, list[Candidate]])
def list_candidates(
    state: Literal["proposed", "suggested", "active", "decayed"] | None = Query(None),
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
    _contract: None = Depends(require_contract),
) -> Any:
    require_org(current_user, org)
    cands = _store.list(state=state)
    return {"candidates": [to_candidate(c) for c in cands]}


@app.get("/candidates/{cand_id}", response_model=Candidate)
def get_candidate(
    cand_id: str,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
    _contract: None = Depends(require_contract),
) -> Candidate:
    require_org(current_user, org)
    cand = _store.get(cand_id)
    if not cand:
        raise HTTPException(404, "Candidate not found")
    return to_candidate(cand)


@app.post("/candidates/{cand_id}/promote", response_model=Candidate)
def promote(
    cand_id: str,
    body: PromoteRequest | None = None,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
    _contract: None = Depends(require_contract),
) -> Candidate:
    require_org(current_user, org)
    target = body.targetState if body else None
    actor = current_user.get("sub", "dev")
    updated = apply_promote(_store, _graph, cand_id, target, actor=actor)
    if not updated:
        raise HTTPException(409, "State conflict or stale promote")
    return to_candidate(updated)


@app.post("/candidates/{cand_id}/reject", response_model=Candidate)
def reject(
    cand_id: str,
    body: RejectRequest | None = None,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
    _contract: None = Depends(require_contract),
) -> Candidate:
    require_org(current_user, org)
    reason = body.reason if body else None
    actor = current_user.get("sub", "dev")
    updated = apply_reject(_store, cand_id, reason, actor=actor)
    if not updated:
        raise HTTPException(404, "Candidate not found")
    return to_candidate(updated)


@app.post("/contradictions/{cid}/resolve", response_model=Candidate)
def resolve_contradiction(
    cid: str,
    body: ResolveRequest,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
    _contract: None = Depends(require_contract),
) -> Candidate:
    require_org(current_user, org)
    actor = current_user.get("sub", "dev")
    updated = apply_resolve(_store, cid, body.resolution, body.keepId, actor=actor)
    if not updated:
        raise HTTPException(422, "Invalid contradiction resolution")
    return to_candidate(updated)


@app.post("/ingest/jsonl", response_model=dict[str, Any])
def ingest_jsonl(
    payload: IngestRequest,
    current_user=Depends(get_current_user),
    org: str = Header("default", alias="X-Praxis-Org"),
    _contract: None = Depends(require_contract),
) -> dict[str, Any]:
    require_org(current_user, org)
    created = 0
    ids: list[str] = []
    provs: list[str] = []
    for f in payload.files:
        content = f.get("content", "")
        for line in content.splitlines():
            if line.strip():
                cid = str(uuid4())
                _store.create(
                    {
                        "id": cid,
                        "title": line[:80],
                        "content": line,
                        "state": "proposed",
                        "confidence": 0.6,
                        "provenance": f.get("name", "ingest") + ":1",
                    }
                )
                created += 1
                ids.append(cid)
                provs.append(f.get("name", "ingest") + ":1")
    return {"candidatesCreated": created, "candidateIds": ids, "provenance": provs}


_EVAL_RESULTS = Path(__file__).parent.parent / "evals" / "results" / "baseline.jsonl"


@app.get("/metrics")
def eval_metrics() -> dict[str, Any]:
    correction_rate: list[float] = []
    sessions: list[str] = []
    corrections_before = 0
    corrections_after = 0

    if _EVAL_RESULTS.exists():
        runs = [json.loads(line) for line in _EVAL_RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]
        by_mode: dict[str, list[dict[str, Any]]] = {}
        for r in runs:
            by_mode.setdefault(r["mode"], []).append(r)
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

    reduction = 0.0
    if corrections_before > 0:
        reduction = (corrections_before - corrections_after) / corrections_before

    return {
        "correction_rate": correction_rate or [0.0],
        "sessions": sessions or ["cold"],
        "corrections_before": corrections_before,
        "corrections_after": corrections_after,
        "reduction_pct": round(reduction, 2),
    }
