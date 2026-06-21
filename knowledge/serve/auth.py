"""Cognito JWT verification + dev seam (PRAXIS_AUTH_DISABLED=1)."""

from __future__ import annotations

import os
from typing import Any

from fastapi import Header, HTTPException


def get_current_user(authorization: str | None = Header(None)) -> dict[str, Any]:
    if os.getenv("PRAXIS_AUTH_DISABLED") == "1":
        return {"sub": "dev-user", "orgs": ["default"]}
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization")
    # TODO: real jose.jwt decode + Cognito JWKS
    token = authorization.split(" ", 1)[1]
    return {"sub": token[:8], "orgs": ["default"]}


def require_org(user: dict[str, Any], org: str) -> None:
    if os.getenv("PRAXIS_AUTH_DISABLED") == "1":
        return
    if org not in user.get("orgs", []):
        raise HTTPException(403, "Not a member of this org")
