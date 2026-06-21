"""Canonical v1 payload builders and header helpers."""

from __future__ import annotations

from typing import Any


def contract_headers(token: str | None = None, org_id: str = "default") -> dict[str, str]:
    h = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Praxis-Contract": "1",
        "X-Praxis-Org": org_id,
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def promote_request(target_state: str | None = None) -> dict[str, Any]:
    return {"targetState": target_state} if target_state else {}


def reject_request(reason: str | None = None) -> dict[str, Any]:
    return {"reason": reason} if reason else {}


def resolve_request(resolution: str, keep_id: str) -> dict[str, Any]:
    return {"resolution": resolution, "keepId": keep_id}
