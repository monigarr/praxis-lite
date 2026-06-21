"""Registry tests — one per on-disk case."""

from __future__ import annotations

import pytest

from knowledge.evals.run import load_case, run_fake


CASES = ["example_add_function", "iambic_poem", "quirky_exhaustive_switch", "quirky_config_load_order"]


@pytest.mark.parametrize("case_id", CASES)
def test_case_loads(case_id: str) -> None:
    case = load_case(case_id)
    assert case.id == case_id


@pytest.mark.parametrize("case_id", CASES)
def test_fake_cold_then_injected(case_id: str) -> None:
    case = load_case(case_id)
    cold = run_fake(case, injected=False)
    inj = run_fake(case, injected=True)
    # Injected should not be worse than cold for these seeded cases
    assert inj.passed or not cold.passed
