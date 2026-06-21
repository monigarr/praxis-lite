"""Schema and loader tests."""

from __future__ import annotations

import pytest

from knowledge.evals.eval_def import EvalCase
from knowledge.evals.run import load_case


def test_example_case_on_disk_loads() -> None:
    case = load_case("example_add_function")
    assert isinstance(case, EvalCase)
    assert case.id == "example_add_function"
    assert case.seeded_insight is not None
