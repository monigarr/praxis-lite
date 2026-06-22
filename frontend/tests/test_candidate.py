"""Unit tests for Candidate model (contract v1 parsing, serialization, state machine)."""

import pytest

from frontend.models.candidate import Candidate


def test_from_mapping_basic() -> None:
    data = {
        "id": "c1",
        "title": "t",
        "content": "c",
        "state": "proposed",
        "confidence": 0.75,
        "provenance": "logs/x:1",
        "createdAt": "2026-06-01T00:00:00Z",
    }
    c = Candidate.from_mapping(data)
    assert c.id == "c1"
    assert c.state == "proposed"
    assert c.created_at == "2026-06-01T00:00:00Z"
    assert c.extra == {}


def test_from_mapping_snake_case_and_extra() -> None:
    data = {
        "id": "c2",
        "title": "t",
        "content": "c",
        "state": "suggested",
        "confidence": "0.9",
        "provenance": "p",
        "created_at": "2026-06-02T00:00:00Z",
        "confidence_breakdown": {"frequency": 0.8},
        "unknown_field": "keep_me",
    }
    c = Candidate.from_mapping(data)
    assert c.created_at == "2026-06-02T00:00:00Z"
    assert c.confidence_breakdown == {"frequency": 0.8}
    assert c.extra == {"unknown_field": "keep_me"}


def test_to_dict_roundtrip() -> None:
    c = Candidate.from_mapping(
        {
            "id": "c3",
            "title": "t",
            "content": "c",
            "state": "active",
            "confidence": 0.6,
            "provenance": "p",
            "createdAt": "2026-06-03T00:00:00Z",
            "auditTrail": [{"action": "promote"}],
        }
    )
    d = c.to_dict()
    assert d["createdAt"] == "2026-06-03T00:00:00Z"
    assert d["auditTrail"] == [{"action": "promote"}]
    assert "unknown" not in d


def test_next_promotion_state_and_low_conf() -> None:
    c = Candidate.from_mapping(
        {"id": "c4", "title": "t", "content": "c", "state": "proposed", "confidence": 0.4, "provenance": "p", "createdAt": "2026-06-01T00:00:00Z"}
    )
    assert c.next_promotion_state() == "suggested"
    assert c.is_low_confidence()
    c.state = "suggested"
    assert c.next_promotion_state() == "active"
    c.state = "active"
    assert c.next_promotion_state() is None
