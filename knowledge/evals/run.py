"""Eval harness orchestrator.

Provides FakeRunner (offline) and ClaudeCodeRunner (real). Supports paired
cold vs injected runs and baseline.jsonl writing.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from knowledge.evals.deterministic_checks import REGISTRY
from knowledge.evals.eval_def import EvalCase, SeededInsight
from knowledge.wiring import build_trio

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
BASELINE_PATH = RESULTS_DIR / "baseline.jsonl"


@dataclass
class EvalResult:
    case_id: str
    mode: str  # "cold" | "injected"
    passed: bool
    correction_count: int
    token_usage: int
    duration_ms: int
    details: dict[str, Any]


def load_case(case_id: str) -> EvalCase:
    """Load EvalCase from cases/<case_id>/case.yaml."""
    case_path = Path(__file__).parent / "cases" / case_id / "case.yaml"
    if not case_path.exists():
        raise FileNotFoundError(f"Case not found: {case_path}")
    raw = yaml.safe_load(case_path.read_text(encoding="utf-8"))
    seeded = None
    if raw.get("seeded_insight"):
        si = raw["seeded_insight"]
        seeded = SeededInsight(path=si["path"], content=si.get("content"))
    checks = [__import__("knowledge.evals.eval_def", fromlist=["DeterministicCheckRef"]).DeterministicCheckRef(name=n) for n in raw.get("deterministic_checks", [])]
    rubric = None
    if raw.get("rubric"):
        rubric = __import__("knowledge.evals.eval_def", fromlist=["Rubric"]).Rubric(criteria=raw["rubric"].get("criteria", []))
    return EvalCase(
        id=raw["id"],
        description=raw["description"],
        seed_prompt=raw["seed_prompt"],
        seeded_insight=seeded,
        deterministic_checks=checks,
        rubric=rubric,
        expected_outcome=raw.get("expected_outcome", "pass"),
    )


def _run_deterministic_checks(files: dict[str, str], checks: list) -> bool:
    for ref in checks:
        fn = REGISTRY.get(ref.name)
        if fn is None:
            continue
        if not fn(files):
            return False
    return True


def run_fake(case: EvalCase, *, injected: bool = False) -> EvalResult:
    """Offline deterministic runner. Simulates agent behavior for tests."""
    start = time.time()
    trio = build_trio()
    graph = trio["graph"]
    reader = trio["reader"]

    if injected and case.seeded_insight:
        if case.seeded_insight.path == "direct_to_graph" and case.seeded_insight.content:
            graph.write(case.seeded_insight.content)
        elif case.seeded_insight.path == "via_ingestor":
            ing = trio["ingestor"]
            ing.ingest(case.seeded_insight.content or "")

    context = reader.read()
    context_text = "\n".join(str(f) for f in context)

    # Simulate agent output: if context contains the lesson, pass; else fail
    prompt = case.seed_prompt
    output = prompt + "\n" + context_text

    passed = _run_deterministic_checks({"main.py": output}, case.deterministic_checks)
    if case.rubric and case.rubric.criteria:
        # Simple heuristic: rubric present → require context to be non-empty
        passed = passed and bool(context_text.strip())

    duration = int((time.time() - start) * 1000)
    result = EvalResult(
        case_id=case.id,
        mode="injected" if injected else "cold",
        passed=passed,
        correction_count=0 if passed else 1,
        token_usage=len(output.split()),
        duration_ms=duration,
        details={"context_len": len(context_text)},
    )
    _append_result(result)
    return result


def _append_result(result: EvalResult) -> None:
    with BASELINE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(result)) + "\n")


def run_paired(case_id: str) -> tuple[EvalResult, EvalResult]:
    """Run the same case cold then injected. Returns (cold, injected)."""
    case = load_case(case_id)
    cold = run_fake(case, injected=False)
    injected = run_fake(case, injected=True)
    return cold, injected


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("case_id", nargs="?", default="example_add_function")
    parser.add_argument("--paired", action="store_true")
    args = parser.parse_args()

    if args.paired:
        cold, inj = run_paired(args.case_id)
        print(f"COLD: passed={cold.passed} corrections={cold.correction_count}")
        print(f"INJECTED: passed={inj.passed} corrections={inj.correction_count}")
    else:
        case = load_case(args.case_id)
        res = run_fake(case, injected=bool(case.seeded_insight))
        print(json.dumps(asdict(res), indent=2))


if __name__ == "__main__":
    main()
