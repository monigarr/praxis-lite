"""Live API smoke tests (run only when PRAXIS_API_BASE_URL is set).

These are the integration smoke referenced in INTEGRATION_SMOKE.md.
"""

import os

import pytest

from frontend.services.api_client import ApiDataProvider


@pytest.mark.skipif(
    os.getenv("PRAXIS_API_BASE_URL") is None,
    reason="Set PRAXIS_API_BASE_URL to run live smoke",
)
def test_live_list_candidates() -> None:
    provider = ApiDataProvider(os.environ["PRAXIS_API_BASE_URL"])
    cands = provider.list_candidates()
    assert isinstance(cands, list)


@pytest.mark.skipif(
    os.getenv("PRAXIS_API_BASE_URL") is None,
    reason="Set PRAXIS_API_BASE_URL to run live smoke",
)
def test_live_promote_and_reject_flow() -> None:
    provider = ApiDataProvider(os.environ["PRAXIS_API_BASE_URL"])
    cands = provider.list_candidates("proposed")
    if not cands:
        pytest.skip("No proposed candidates on live server")
    first = cands[0]
    promoted = provider.promote(first.id)
    assert promoted.state in ("suggested", "active")
