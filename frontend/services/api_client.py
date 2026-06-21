"""Live API client for the candidate contract (v1)."""

from __future__ import annotations

import os
from typing import Any

import httpx

from ..models.candidate import Candidate, PromotionState
from .data_provider import DataProvider


class ApiClientError(RuntimeError):
    """Raised for 4xx/5xx responses with helpful context for the dashboard."""


class ApiDataProvider(DataProvider):
    """HTTP implementation of DataProvider.

    Requires PRAXIS_API_BASE_URL. Uses PRAXIS_API_TOKEN and PRAXIS_ORG_ID when present.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = os.getenv("PRAXIS_API_TOKEN")
        self.org_id = os.getenv("PRAXIS_ORG_ID", "default")
        self.headers = self._contract_headers()

    def _contract_headers(self) -> dict[str, str]:
        h = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Praxis-Contract": "1",
            "X-Praxis-Org": self.org_id,
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _request(self, method: str, path: str, json: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.request(method, url, headers=self.headers, json=json, timeout=10.0)
        except httpx.RequestError as exc:
            raise ApiClientError(f"Network error calling {url}: {exc}") from exc
        if resp.status_code >= 400:
            raise ApiClientError(f"{resp.status_code} from {path}: {resp.text}")
        return resp.json() if resp.text else None

    # ------------------------------------------------------------------ queries
    def list_candidates(self, state: PromotionState | None = None) -> list[Candidate]:
        qs = f"?state={state}" if state else ""
        data = self._request("GET", f"/candidates{qs}")
        items = data.get("candidates", data) if isinstance(data, dict) else data
        return [Candidate.from_mapping(item) for item in items]

    def get_candidate(self, candidate_id: str) -> Candidate | None:
        try:
            data = self._request("GET", f"/candidates/{candidate_id}")
            return Candidate.from_mapping(data)
        except ApiClientError as exc:
            if "404" in str(exc):
                return None
            raise

    # ------------------------------------------------------------------ mutations
    def promote(self, candidate_id: str, target_state: PromotionState | None = None) -> Candidate:
        body: dict[str, Any] = {}
        if target_state:
            body["targetState"] = target_state
        data = self._request("POST", f"/candidates/{candidate_id}/promote", json=body or None)
        return Candidate.from_mapping(data)

    def reject(self, candidate_id: str, reason: str | None = None) -> Candidate:
        body = {"reason": reason} if reason else {}
        data = self._request("POST", f"/candidates/{candidate_id}/reject", json=body or None)
        return Candidate.from_mapping(data) if data else self.get_candidate(candidate_id)  # type: ignore[return-value]

    def resolve_contradiction(
        self, primary_id: str, rival_id: str, resolution: str, keep_id: str
    ) -> Candidate:
        body = {"resolution": resolution, "keepId": keep_id}
        cid = f"{primary_id}__{rival_id}"
        data = self._request("POST", f"/contradictions/{cid}/resolve", json=body)
        return Candidate.from_mapping(data)
