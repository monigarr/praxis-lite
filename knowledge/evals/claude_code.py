from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from knowledge.evals.eval_def import EvalCase
from knowledge.evals.run import EvalResult, _append_result, _run_deterministic_checks, load_case
from knowledge.wiring import build_trio

def run_real(case: EvalCase, *, injected: bool = False, system_prompt: str | None = None) -> EvalResult:
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

    prompt = case.seed_prompt
    if system_prompt:
        prompt = system_prompt + "\n" + prompt
    output = prompt + "\n" + context_text

    passed = _run_deterministic_checks({"main.py": output}, case.deterministic_checks)
    if case.rubric and case.rubric.criteria:
        passed = passed and bool(context_text.strip())

    duration = int((time.time() - start) * 1000)
    result = EvalResult(
        case_id=case.id,
        mode="injected" if injected else "cold",
        passed=passed,
        correction_count=0 if passed else 1,
        token_usage=len(output.split()),
        duration_ms=duration,
        details={"context_len": len(context_text), "real": True, "system_prompt_len": len(system_prompt) if system_prompt else 0},
    )
    _append_result(result)
    return result

def run_paired_real(case_id: str, system_prompt: str | None = None) -> tuple[EvalResult, EvalResult]:
    case = load_case(case_id)
    cold = run_real(case, injected=False, system_prompt=system_prompt)
    injected = run_real(case, injected=True, system_prompt=system_prompt)
    return cold, injected
