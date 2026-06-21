# Monica Peters — Dashboard As-Built Spec

**Lite version context:** This repo (`praxis-lite`) is a solo implementation and maintenance effort by Monica Peters. It is inspired by the original PRAXIS multi-pillar architecture but is developed independently. See [docs/plans/PRAXIS_Project_Plan.html](../plans/PRAXIS_Project_Plan.html) for the locked architecture, Lite framing, and **🎯 Capstone Alignment (PRD)** box.

**Author:** Monica Peters <monigarr@MoniGarr.com>  
**Branch:** `monica/dashboard-human-gate`  
**Created:** 2026-06-17  
**Last updated:** 2026-06-19  
**Status:** As-built through Day 8 on mock — React UI shipped; Python contract layer in `frontend/`; live E2E when the candidate API is implemented in `knowledge/serve/`.

Architecture source of truth: [PRAXIS_Project_Plan.html](../plans/PRAXIS_Project_Plan.html).

Pillar architecture: [ARCHITECTURE_MONICA.md](ARCHITECTURE_MONICA.md).

## Overview

The human-gate **dashboard UI** is a **Vite + React + TypeScript** app under `frontend-react/`. Entry point `src/App.tsx` wires filters, selection, and API providers to UI components.

The **Python contract layer** under `frontend/` holds typed models, mock fixtures, `DataProvider` protocol, and pytest — not a presentation runtime.

```text
frontend-react/src/App.tsx
  → layout: Refresh · filters · environment badge
  → components/CandidateTable.tsx, CandidateCards.tsx
  → components/CandidateDetail.tsx
  → components/ContradictionPanel.tsx
  → components/EvalMetricsEmbed.tsx
  → components/graph/KnowledgeGraphView.tsx
  → api/apiClient.ts, mockProvider.ts, providerFactory.ts

frontend/  (contract + mock — no UI)
  → models/candidate.py
  → services/data_provider.py, api_client.py, mock_provider.py
  → mock_data.py  →  exported to public/mock-candidates.json
  → tests/
```

Lifecycle states: `proposed → suggested → active` (plus `decayed` and unrecognized API values preserved for display).

## Screen 1: Dashboard shell + candidate list (shipped)

**Files:** `frontend-react/src/App.tsx`, `CandidateTable.tsx`, `CandidateCards.tsx`, `layout/FilterBar.tsx`

| Element | Implementation |
|---------|----------------|
| Header | `DashboardHeader` — title + subtitle |
| Mode banner | Mock vs live API badge from `VITE_PRAXIS_API_BASE_URL` |
| Sidebar / toolbar | **Refresh data** — reloads provider and candidate list |
| Search | Text filter on title and content (case-insensitive) |
| State filter | Select — All / proposed / suggested / active / decayed |
| Global selection | Shared selection drives detail view + table/card actions |
| Table view | Sortable columns; confidence progress; promote/reject with confirmations |
| Card view | Grid layout; **Inspect in detail** sets global selection |
| State badge | `StateBadge` — color-coded lifecycle states |
| Confidence | Progress bar on cards; numeric column in table |
| Provenance | Caption with `` `logs/<file>.jsonl:<line>` `` |
| Actions | Confirm dialogs; optional **reject reason**; low-confidence promote warning below **50%**; success banner; decayed blocked from promote |
| Error states | Empty filter message; API load failure banner |
| Footer | Pillar + integration note |

**Mock data:** 17+ candidates in `frontend/mock_data.py`, exported to `frontend-react/public/mock-candidates.json`. Includes `confidenceBreakdown` on cand_1–3, contradiction pair cand_9 ↔ cand_16, and decayed cand_12.

## Screen 2: Candidate detail (Day 3 — shipped)

**File:** `frontend-react/src/components/CandidateDetail.tsx`

| Element | Implementation |
|---------|----------------|
| Container | Detail panel synced with global selection |
| Content | Full title, state, provenance, body |
| Confidence | `ConfidenceBreakdown.tsx` — frequency/recency/breadth metrics + tooltips |
| Audit trail | Renders `auditTrail` entries with JSONL provenance links |
| Extra fields | Pipeline-only keys (excludes auditTrail duplicate) |
| Contradictions | `ContradictionPanel.tsx` with keep primary / keep rival / defer actions |

## Screen 3: Eval metrics embed (Day 8 — shipped)

**File:** `frontend-react/src/components/EvalMetricsEmbed.tsx`

- Collapsible section with correction-rate line chart.
- `VITE_PRAXIS_EVAL_METRICS_URL` → Dominic JSON endpoint; placeholder when unset.
- Optional before/after correction scoreboard when API returns those fields.

## Screen 4: Knowledge graph explorer (shipped)

**Files:** `frontend-react/src/components/graph/KnowledgeGraphView.tsx`, `GraphExplorer.tsx`

- Scope tree and relationship visualization from `public/mock-graph.json` (exported with candidates).
- Complements list/detail review for demo narrative.

## Data contract (forward-compatible)

`frontend/models/candidate.py` — `Candidate.from_mapping()` is the Python integration surface. React types mirror the same shape in `frontend-react/src/types/candidate.ts`. **Canonical contract:** [candidate-api-v1.md](../integration/candidate-api-v1.md).

### Required for display (defaults if absent)

| Field | Aliases accepted | Notes |
|-------|------------------|-------|
| `id` | — | Stable identifier |
| `title` | — | Distilled lesson title |
| `content` | — | Full lesson body |
| `state` | — | Known: `proposed`, `suggested`, `active`, `decayed`; unknown values shown as-is (gray badge) |
| `confidence` | — | Float 0–1; defaults to `0.0` |
| `provenance` | `source`, `source_log`, `sourceLog` | Canonical display: `logs/<file>.jsonl:<line>` |
| `createdAt` | `created_at`, `updatedAt`, `updated_at` | ISO 8601 |

### Optional (pipeline extensions)

| Field | Aliases | Notes |
|-------|---------|-------|
| `confidenceBreakdown` | `confidence_breakdown` | `{ frequency, recency, breadth }` + optional rationale strings |
| `contradictions` | `contradiction_ids` | List of ids or `{ id }` objects |
| `auditTrail` | `audit_trail` | List of `{ action, timestamp, provenance, actor, note? }` |
| *any other key* | — | Preserved in `Candidate.extra` / TS extended fields and shown in detail view |

**Versioning:** `VITE_PRAXIS_CONTRACT_VERSION` env (default `1`); HTTP client sends `X-Praxis-Contract` header. Matthew/Dominic may extend the schema; Monica's pillar must not break on unknown fields.

### Mutations (canonical v1 — `docs/integration/candidate-api-v1.md`)

| Action | Endpoint | Body |
|--------|----------|------|
| Promote | `POST /candidates/{id}/promote` | `{ "targetState": "suggested" \| "active" }` → updated candidate |
| Reject | `POST /candidates/{id}/reject` | `{ "reason"?: string }` |
| Resolve contradiction | `POST /contradictions/{id}/resolve` | `{ "resolution": "keep_a" \| "keep_b", "keepId": string }` → kept candidate |

Contradiction id: `{primaryId}__{rivalId}`. UI maps "Keep this candidate" → `keep_a`, rival → `keep_b` in `contract_v1.py` / React API helpers.

409 responses surface as user-visible conflict messages (refresh + retry). Promote retries with `{}` if server rejects explicit `targetState`.

## Python contract layer (`frontend/`)

Parallel typed client for pytest and Matthew's server validation — same contract, same mock fixtures.

| Element | Implementation |
|---------|----------------|
| Models | `frontend/models/candidate.py` — `Candidate.from_mapping()` |
| Provider | `frontend/services/data_provider.py` — factory by env |
| API client | `frontend/services/api_client.py` — contract v1 HTTP |
| Mock | `frontend/services/mock_provider.py` + `mock_data.py` |
| Tests | `frontend/tests/` — contract fixtures, gate workflow, live API smoke |

Run: `uv run pytest frontend/tests/ -q`. Sync JSON: `python scripts/export-mock-candidates.py`.

## Design notes

- React + CSS modules / index.css — custom layout and branding
- Keyboard: Tab to selection controls; `aria-label` on promote/reject/inspect/defer
- Deploy: `frontend-react/render.yaml` — see [RENDER_DEPLOY.md](RENDER_DEPLOY.md)

## Remaining (Days 9–10)

See [DAYS_9_10_REMAINING.md](DAYS_9_10_REMAINING.md) — demo rehearsal checklist, user-flow video, screen-reader pass.
