"""Demo helpers for Acts 1 & 3 (quirky benchmark wiring).

Act 1 (cold): run quirky cases without seeded insight.
Act 3 (smart): run same cases with insight injected and show metrics.
"""

from __future__ import annotations

from knowledge.evals.run import load_case, run_fake, run_paired


def act1_cold(case_ids: list[str] | None = None) -> dict[str, int]:
    cases = case_ids or ["quirky_exhaustive_switch", "quirky_config_load_order"]
    results = {}
    for cid in cases:
        case = load_case(cid)
        res = run_fake(case, injected=False)
        results[cid] = res.correction_count
    return results


def act3_injected(case_ids: list[str] | None = None) -> dict[str, int]:
    cases = case_ids or ["quirky_exhaustive_switch", "quirky_config_load_order"]
    results = {}
    for cid in cases:
        case = load_case(cid)
        res = run_fake(case, injected=True)
        results[cid] = res.correction_count
    return results


if __name__ == "__main__":
    print("Act 1 (cold):", act1_cold())
    print("Act 3 (injected):", act3_injected())
