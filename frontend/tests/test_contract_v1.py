"""Unit tests for contract_v1 helpers (headers and request builders)."""

from frontend.services.contract_v1 import contract_headers, promote_request, reject_request, resolve_request


def test_contract_headers_with_token() -> None:
    h = contract_headers("tok123", "orgX")
    assert h["X-Praxis-Contract"] == "1"
    assert h["Authorization"] == "Bearer tok123"
    assert h["X-Praxis-Org"] == "orgX"


def test_contract_headers_no_token() -> None:
    h = contract_headers()
    assert "Authorization" not in h


def test_promote_request() -> None:
    assert promote_request("active") == {"targetState": "active"}
    assert promote_request() == {}


def test_reject_and_resolve() -> None:
    assert reject_request("bad") == {"reason": "bad"}
    assert resolve_request("keep_a", "id1") == {"resolution": "keep_a", "keepId": "id1"}
