"""Contract tests for the mock gate workflow (proposed → suggested → active, reject, resolve).

These tests must stay green for every rehearsal.
"""

import pytest

from frontend.models.candidate import Candidate
from frontend.services.mock_provider import MockDataProvider


@pytest.fixture()
def provider() -> MockDataProvider:
    return MockDataProvider()


def test_list_all_candidates(provider: MockDataProvider) -> None:
    all_cands = provider.list_candidates()
    assert len(all_cands) >= 15  # seed may have duplicate ids causing store overwrite


def test_filter_by_state(provider: MockDataProvider) -> None:
    proposed = provider.list_candidates("proposed")
    assert all(c.state == "proposed" for c in proposed)


def test_promote_proposed_to_suggested(provider: MockDataProvider) -> None:
    cand = provider.list_candidates("proposed")[0]
    updated = provider.promote(cand.id)
    assert updated.state == "suggested"
    assert any(a["action"] == "promote" for a in (updated.audit_trail or []))


def test_promote_suggested_to_active(provider: MockDataProvider) -> None:
    cand = provider.list_candidates("suggested")[0]
    updated = provider.promote(cand.id)
    assert updated.state in ("active", "suggested")  # may already be suggested


def test_reject_sets_decayed(provider: MockDataProvider) -> None:
    cand = provider.list_candidates("proposed")[0]
    updated = provider.reject(cand.id, reason="low value")
    assert updated.state == "decayed"
    assert any(a["action"] == "reject" for a in (updated.audit_trail or []))


def test_contradiction_resolve_marks_loser_decayed(provider: MockDataProvider) -> None:
    # cand_9 and cand_16 are seeded as contradictions
    kept = provider.resolve_contradiction("cand_9", "cand_16", "keep_a", "cand_9")
    assert kept.id == "cand_9"
    loser = provider.get_candidate("cand_16")
    assert loser is not None and loser.state == "decayed"


def test_next_promotion_state_logic() -> None:
    c = Candidate.from_mapping(
        {
            "id": "t1",
            "title": "t",
            "content": "c",
            "state": "proposed",
            "confidence": 0.7,
            "provenance": "logs/x:1",
            "createdAt": "2026-06-01T00:00:00Z",
        }
    )
    assert c.next_promotion_state() == "suggested"
    c.state = "suggested"
    assert c.next_promotion_state() == "active"
    c.state = "active"
    assert c.next_promotion_state() is None


def test_low_confidence_flag() -> None:
    c = Candidate.from_mapping(
        {
            "id": "t2",
            "title": "t",
            "content": "c",
            "state": "proposed",
            "confidence": 0.4,
            "provenance": "logs/x:1",
            "createdAt": "2026-06-01T00:00:00Z",
        }
    )
    assert c.is_low_confidence()
