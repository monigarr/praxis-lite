# PRAXIS Lite

**Self-Improving Knowledge Loop for Claude Code Agents with Human-in-the-Loop Governance**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render)](https://render.com)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Intended Use Cases](#intended-use-cases)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Running the Application](#running-the-application)
- [Running All Tests](#running-all-tests)
- [Deployment](#deployment)
  - [Render.com (Recommended)](#rendercom-recommended)
  - [Local Docker](#local-docker)
- [Configuration](#configuration)
- [API Contracts & Integration](#api-contracts--integration)
- [Usage Guide](#usage-guide)
  - [Human Gate Dashboard](#human-gate-dashboard)
  - [Knowledge Pipeline & Evals](#knowledge-pipeline--evals)
- [Contributing](#contributing)
- [Security & Compliance](#security--compliance)
- [Troubleshooting](#troubleshooting)
- [Team & Support](#team--support)
- [License](#license)
- [Roadmap](#roadmap)

---

## Project Overview

PRAXIS (Prompt-Response Agent eXperience Improvement System) Lite is the reference implementation of a **self-improving knowledge graph (KG) system** tailored for Claude Code agents operating inside the Gauntlet AI ecosystem.

The system closes the loop between agent sessions and organizational knowledge by:

1. Capturing rich session data (via `session-capture`)
2. Ingesting, distilling, and clustering learning moments into a living KG (`knowledge/`)
3. Exposing candidate proposals through a governed REST API
4. Providing a **Human Gate Dashboard** (`frontend-react/`) for architects, engineers, and domain experts to review, promote, contradict, or decay candidates before they enter the canonical graph

**Core value proposition:** Turn every Claude Code session into compounding organizational intelligence while maintaining strict human oversight and provenance.

This repository (`praxis-lite`) is the canonical, production-scaffolded slice used for the June 2026 Gauntlet capstone showcase.

---

## Intended Use Cases

- **Agent teams** running Claude Code on real codebases who want session memory that survives context windows.
- **Platform / MLOps teams** needing auditable, human-gated knowledge promotion pipelines.
- **Enterprise knowledge programs** requiring provenance, contradiction detection, and eval harnesses before trusting LLM outputs.
- **Security & compliance teams** who need session replay, deterministic checks, and policy redaction before graph writes.

**Not intended for:** General-purpose chatbots, non-Claude agents, or fully autonomous (no-human) knowledge systems.

---

## Architecture

PRAXIS follows a strict three-pillar model with clear ownership and contract boundaries:

| Pillar | Location | Maturity | Key Components |
|--------|----------|----------|----------------|
| **Dashboard & Human Gate** | `frontend-react/`, `frontend/` | High (demo-ready on mock) | React 19 + Vite dashboard, Python contract layer, mock/live API client, state machine (`proposed → suggested → active → decayed`) |
| **ML & Knowledge Pipeline** | `knowledge/` | Scaffolding (core graph + ingest live) | InMemoryGraph + vector, Ingestors (prompt/JSONL/heuristic), write policies (cluster/dedupe/conflict/score/decay), FastAPI candidate service |
| **Architecture, Eval & Integration** | `knowledge/evals/`, `session-capture/`, `infra/` | Partial | YAML-driven eval harness + deterministic checks, Go `claude+` PTY capture to DynamoDB, AWS CDK infra |

**Integration contracts** (v1) are the source of truth:
- `docs/integration/candidate-api-v1.md`
- `docs/integration/eval-metrics-v1.md`

All pillars respect the **no-cross-import rule** between `frontend/` and `knowledge/`.

---

## Repository Structure

```text
praxis-lite/
├── frontend/                  # Python contract models, services, mock data, pytest (11 tests)
├── frontend-react/            # React 19 + Vite + TS human-gate dashboard (contract v1 client)
├── knowledge/                 # Core KG, ingestion, graph readers, wiring
│   ├── serve/                 # FastAPI candidate API (auth, store, pipeline adapter)
│   ├── knowledge_graph/       # ABC + InMemory + vector impl + write policies
│   ├── ingestion/             # Ingestor ABC + variants
│   ├── graph_reader/          # WholeFileReader, retrieving variants
│   ├── evals/                 # YAML cases, FakeRunner, ClaudeCodeRunner, deterministic checks
│   └── run.py                 # Dev entrypoint (build_trio + eval smoke)
├── session-capture/           # Go claude+ daemon (PTY, JSONL tail, DynamoDB writer)
├── infra/                     # AWS CDK (DynamoDB sessions table)
├── docs/                      # Plans, integration contracts, fixtures, wire-up guides
├── scripts/                   # Utility scripts
├── .env.example
├── Dockerfile
├── render.yaml
├── pyproject.toml             # uv + pytest + ruff + mypy config
├── uv.lock
└── .gitlab-ci.yml             # SAST + secret detection (extend for full CI)
```

---

## Prerequisites

- **Python**: 3.12+ (required by `pyproject.toml`)
- **uv**: Modern Python package manager (recommended over pip/venv)
- **Node.js**: 18+ and npm (for `frontend-react/`)
- **Docker**: 24+ (for containerized runs or Render)
- **Git**: For cloning and contributing
- **Optional**: Go 1.21+ (to build/test `session-capture/`), AWS CLI + CDK (for `infra/`)

**Hardware baseline** (dev laptop reference): Intel i9-12900H, 64 GB RAM, NVIDIA RTX 3080 (for local LLM evals if desired).

---

## Local Development Setup

```bash
# 1. Clone
git clone https://labs.gauntletai.com/monicapeters/praxis-lite.git
cd praxis-lite

# 2. Python environment (uv)
uv sync --dev          # installs from pyproject.toml + dev deps
# or: uv pip install -e .[dev]

# 3. React frontend
cd frontend-react
npm install
cd ..

# 4. Environment
cp .env.example .env
# Edit .env with your values (see Configuration section)
```

**Activate shell**: `uv shell` or use `uv run <cmd>` for all subsequent commands.

---

## Running the Application

### Backend (Candidate API)

```bash
uv run uvicorn knowledge.serve.app:app --reload --port 8000
```

- OpenAPI docs: http://localhost:8000/docs
- Health: `GET /health` (when implemented)
- Dev mode: set `PRAXIS_AUTH_DISABLED=1`

### Frontend Dashboard (React)

```bash
cd frontend-react
npm run dev
```

- Default: http://localhost:5173
- Configure `VITE_PRAXIS_API_BASE_URL=http://localhost:8000` in `.env` (or use mock mode when unset)

### Full Stack (recommended for local)

Use two terminals or a process manager (e.g., concurrently or Render local).

### Knowledge Pipeline Smoke

```bash
uv run python -m knowledge.run
# or: uv run python knowledge/run.py
```

### Evals Harness

```bash
uv run python -m knowledge.evals.run
# or: uv run python knowledge/evals/run.py
```

---

## Running All Tests

### Python Tests (pytest)

```bash
# All tests (knowledge + frontend)
uv run pytest

# Verbose + coverage (if pytest-cov added)
uv run pytest -v --cov=knowledge --cov=frontend

# Specific pillar
uv run pytest knowledge/tests/
uv run pytest frontend/tests/
uv run pytest knowledge/evals/tests/
```

**Current status (as of 2026-06-21):** 30+ Python tests passing under the configured `pythonpath = ["."]`.

**Note:** Some legacy runs required `PYTHONPATH=frontend`; the `pyproject.toml` now handles this.

### React / TypeScript Checks

```bash
cd frontend-react
npm run build          # runs tsc + vite build (type + build check)
```

No unit tests yet in React (add Vitest + React Testing Library when expanding).

### Full Quality Gate (manual)

```bash
uv run ruff check .
uv run mypy .
cd frontend-react && npm run build
```

---

## Deployment

### Render.com (Recommended)

The repo includes a Render Blueprint (`render.yaml`).

1. Connect the GitLab repo (or GitHub mirror) to Render.
2. Render auto-detects `render.yaml` and provisions:
   - `praxis-lite` web service (Docker, `starter` plan, autoDeploy on `main`)
3. Set required env vars in Render dashboard (see Configuration).
4. (Future) Add static site for `frontend-react/` build.

**Current limitation:** Dockerfile is a placeholder. Update `CMD` to `uvicorn knowledge.serve.app:app --host 0.0.0.0 --port $PORT` once the service is primary.

### Local Docker

```bash
docker build -t praxis-lite .
docker run -p 8000:8000 --env-file .env praxis-lite
```

Override CMD for the React build or multi-service compose as the system matures.

**Render vs local parity:** Use the same `PRAXIS_ENV=production` and secrets.

---

## Configuration

All configuration via environment variables (never commit secrets).

| Variable | Purpose | Default / Example |
|----------|---------|-------------------|
| `PRAXIS_ENV` | `development` / `production` | `development` |
| `PRAXIS_LOG_LEVEL` | Logging verbosity | `INFO` |
| `PRAXIS_AUTH_DISABLED` | Disable JWT for local dev | `0` (set `1` for mock) |
| `PRAXIS_DB_URL` | Postgres connection (future) | `postgresql://...` |
| `VITE_PRAXIS_API_BASE_URL` | Dashboard → API base (React) | `http://localhost:8000` or unset for mock |
| `VITE_PRAXIS_EVAL_METRICS_URL` | Eval metrics embed endpoint | (future) |
| `RENDER_API_KEY` | Render automation (CI) | — |
| `GITLAB_TOKEN` / `GITHUB_TOKEN` | Mirror automation (CI only) | — |

Copy `.env.example` and never commit `.env`.

---

## API Contracts & Integration

**Source of truth:** `docs/integration/`

- **Candidate API v1**: `GET /candidates`, `POST /candidates/{id}/promote`, `POST /candidates/{id}/contradict`, etc.
  - Header: `X-Praxis-Contract: 1`
  - Client retry logic: 409 (conflict) → refresh, 400/422 → promote with `{}` body fallback
- **Eval Metrics v1**: Prometheus-style or JSON endpoint for dashboard embed

**Contract tests** live in `frontend/tests/test_contract_fixtures.py` and validate against `docs/integration/fixtures/*.json`.

**Wire-up guide:** See `docs/integration/wire-up.md` (self-serve checklist for new pillar owners).

---

## Usage Guide

### Human Gate Dashboard

1. Start backend + frontend (see above).
2. In mock mode (no `VITE_PRAXIS_API_BASE_URL`): 17 seed candidates from `frontend/mock_data.py`.
3. In live mode: Candidates flow from `knowledge/serve/candidate_store.py` (InMemoryGraph → CandidateStore).
4. Actions: Promote (→ active), Contradict (pairwise flag), View confidence breakdown, Eval embed.
5. State machine enforces: `proposed → suggested → active | decayed`.

**For non-technical stakeholders:** The dashboard is the single pane of glass. No CLI required.

### Knowledge Pipeline & Evals

- **Ingest**: Use `PromptIngestor`, `JSONLIngestor`, or `HeuristicMomentIngestor`.
- **Graph ops**: `InMemoryGraph` + vector index; write policies run on every mutation.
- **Evals**: Define cases in YAML under `knowledge/evals/cases/`. Run with `FakeRunner` (offline) or `ClaudeCodeRunner` (credit-consuming).
- **Deterministic checks**: `builds.py`, `poetry.py` ensure repo health before promotion.

**For architects / MLOps**: Extend `knowledge_graph/write_policy/` or add new deterministic checks.

---

## Contributing

We follow conventional commits and small, focused merge requests.

1. Create feature branch from `main` (or pillar branch).
2. Run full test + lint gate before push.
3. Reference GitLab issues with `#<number>`.
4. Update relevant docs in `docs/` when behavior or contracts change.
5. For cross-pillar work, coordinate via standup (see `docs/STANDUP_TEMPLATE.md`).

**Pre-commit quality**: `ruff`, `mypy`, `tsc`, contract tests.

See `.cursor/rules/` for team coding standards.

---

## Security & Compliance

- **Auth**: Cognito JWT (stub) or disabled for local. Never run production with `PRAXIS_AUTH_DISABLED=1`.
- **Provenance**: Every candidate carries `provenance` (required field).
- **Redaction & Policy**: `write_policy/redactor.py` runs before any graph write.
- **Session capture**: All Claude Code PTY sessions logged to DynamoDB with JSONL tailing.
- **SAST / Secret Detection**: GitLab CI includes official templates; extend with dependency & container scanning.
- **Data residency**: Default is in-memory; production path uses Postgres + DynamoDB (infra/).

Report vulnerabilities via private GitLab issue or monigarr@monigarr.com.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `pytest` fails with import errors | PYTHONPATH not set | Use `uv run pytest` (pyproject.toml handles it) |
| React can't reach API | CORS or wrong `VITE_PRAXIS_API_BASE_URL` | Check browser console; set env and restart Vite |
| 409 on promote | Concurrent candidate edit | Client auto-refreshes list |
| Docker CMD does nothing useful | Placeholder in Dockerfile | Update to real service entrypoint |
| Go tests skipped | `go` not installed | Install Go 1.21+ or skip `session-capture/` locally |
| Render deploy fails | Dockerfile not updated for web service | Align `CMD` with uvicorn or multi-stage |

**Health check command**: `curl http://localhost:8000/health` (implement when adding router).

---

## Team & Support

**This repository is a solo project.**  
`praxis-lite` is designed, implemented, and maintained solely by **Monica Peters** as an independent capstone implementation. It draws architectural inspiration from the original PRAXIS multi-pillar concepts but is developed and owned independently.

- **Primary repo**: https://labs.gauntletai.com/monicapeters/praxis-lite
- **Mirror**: https://github.com/monigarr/praxis-lite
- **Project Plan**: `docs/plans/PRAXIS_Project_Plan.html`
- **Integration Contracts & Wire-up**: `docs/integration/`

For collaborators or non-technical stakeholders: Start with the dashboard (`frontend-react/`) and the Project Plan HTML (visual architecture + PRD box). All contributions or questions should be directed to the repository owner.

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Roadmap

See `docs/plans/PRAXIS_Project_Plan.html` §Capstone Alignment and `PLAN_ALIGNMENT_GAP_CHECKLIST.md` for current sprint gates.

**Near-term (post-demo)**:
- Full candidate REST API with Postgres persistence
- Eval metrics HTTP endpoint for dashboard embed
- React unit tests + CI gate
- Production Dockerfile + health/readiness probes
- Compounding-curve measurement harness

**Longer-term**:
- Multi-tenant org isolation
- VCS-agnostic promotion replay
- Self-hosted vs Render options matrix

---

*Last updated: 2026-06-21 — aligned to `monica/dashboard-human-gate` branch and full-repo audit.*
*This README is the single source of truth for onboarding. Update it when contracts, runbooks, or deployment paths change.*
