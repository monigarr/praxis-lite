# Dominic Demo Data Bundle

Artifacts for the Jun 29 Gauntlet showcase.

## Contents

- `act_runner.py` — helpers for Act 1 (cold) and Act 3 (injected) quirky benchmark runs.
- `generate_curve.py` — produces `docs/integration/fixtures/eval-metrics.json` with ≥50% reduction data.
- `baseline.jsonl` (generated) — raw EvalResult rows from paired runs.

## Quick commands

```powershell
# Run paired quirky cases (cold + injected)
python -m knowledge.evals.run --paired quirky_exhaustive_switch

# Generate fresh curve fixture
python -m knowledge.evals.demo.generate_curve

# Start API with metrics endpoint
uvicorn knowledge.serve.app:app --reload
# GET http://localhost:8000/metrics
```

## Contract

Metrics endpoint returns the shape defined in `docs/integration/eval-metrics-v1.md`.
Dashboard consumes it when `PRAXIS_EVAL_METRICS_URL` is set.
