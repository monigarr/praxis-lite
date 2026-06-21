"""DataProvider protocol and environment-based factory."""

from __future__ import annotations

import os
from typing import Protocol

from ..models.candidate import Candidate, PromotionState


class DataProvider(Protocol):
    """Abstract provider used by the dashboard and contract tests."""

    def list_candidates(self, state: PromotionState | None = None) -> list[Candidate]: ...
    def get_candidate(self, candidate_id: str) -> Candidate | None: ...
    def promote(self, candidate_id: str, target_state: PromotionState | None = None) -> Candidate: ...
    def reject(self, candidate_id: str, reason: str | None = None) -> Candidate: ...
    def resolve_contradiction(
        self, primary_id: str, rival_id: str, resolution: str, keep_id: str
    ) -> Candidate: ...


def make_provider() -> DataProvider:
    """Factory that chooses mock vs live API based on environment.

    Set PRAXIS_API_BASE_URL to use the live client; otherwise returns the mock.
    """
    base_url = os.getenv("PRAXIS_API_BASE_URL")
    if base_url:
        from .api_client import ApiDataProvider

        return ApiDataProvider(base_url=base_url)
    from .mock_provider import MockDataProvider

    return MockDataProvider()
