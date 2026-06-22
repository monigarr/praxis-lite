# Architectural Blueprint

## Project: PRAXIS Lite
### Classification: Open-Source Capstone Reference Implementation
### Author: Gauntlet AI Capstone Team (Monica Peters, Matthew Daw, Dominic Antonelli)
### Sprint: June 2026

---

## 1. Architectural Philosophy: Contract-Driven, Human-Gated, Self-Improving KG

PRAXIS Lite implements a **three-pillar, contract-first architecture** for a self-improving knowledge graph (KG) tailored to Claude Code agents. Rather than a monolithic application, the system is deliberately decoupled into independent pillars that communicate exclusively through versioned integration contracts (`docs/integration/*-v1.md`) or explicit mock fixtures.

Key principles:
- **No-Cross-Import Rule:** `frontend/` and `frontend-react/` never import from `knowledge/` (enforced and verified in contract tests).
- **Human Gate as First-Class Citizen:** Every candidate promotion, contradiction, or decay decision requires explicit human action via the React dashboard; full provenance and audit trail.
- **MCP & Agent-Native Tooling:** The architecture is designed to be readable, maintainable, and safely extended by AI developer tools (Cursor, Claude Code, automated agents) using the Model Context Protocol (MCP) patterns for structured context and tool calling.
- **Ephemeral & Portable:** Stateless where possible; Docker-first local run; Render.com zero-config deploy; optional AWS CDK for persistence layer.

---

## 2. Three-Pillar Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Human Gate Layer                         │
│  frontend-react/ (React 19 + Vite + TS) + frontend/ (contracts) │
│  - Dashboard UI (promote/contradict/decay)                      │
│  - State machine (proposed → suggested → active → decayed)      │
│  - Mock + live API client (ApiDataProvider)                     │
│  - Contract tests (pytest, 11 passing)                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │ REST / JSON contracts (v1)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Pipeline Layer                     │
│  knowledge/ (Python + FastAPI)                                  │
│  - InMemoryGraph + vector store                                 │
│  - Ingestion (prompt/JSONL/heuristic)                           │
│  - Write policies (cluster/dedupe/conflict/score/decay)         │
│  - Candidate API (GET/POST /candidates/*) — critical path       │
│  - Eval harness (YAML cases, deterministic checks)              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Capture & Infrastructure Layer                  │
│  session-capture/ (Go) + infra/ (AWS CDK)                       │
│  - claude+ PTY wrapper → JSONL → DynamoDB                       │
│  - Sessions table (CDK)                                         │
│  - Eval runners + metrics endpoint                              │
└─────────────────────────────────────────────────────────────────┘
```

**Integration contracts are the source of truth** — see `docs/integration/candidate-api-v1.md` and `docs/integration/eval-metrics-v1.md`.

---

## 3. Layered Component Breakdown

### A. Dashboard & Human Gate (`frontend-react/`, `frontend/`)
- React 19 + Vite + TypeScript SPA with modern tooling (Vitest, Testing Library).
- Python contract layer (`frontend/`) provides Pydantic models, state machine, mock data, and `ApiDataProvider` (stdlib urllib, retry logic).
- Supports mock mode (for rapid demo) and live mode (toggle to real candidate API).
- Enforces provenance on every `Candidate`; handles contradiction pairs and decay.

### B. ML & Knowledge Pipeline (`knowledge/`)
- Core abstractions: `KnowledgeGraph` ABC, `InMemoryGraph`, vector-backed variants.
- Ingestion pipeline with pluggable ingestors.
- Write policies enforce clustering, deduplication, conflict detection, scoring, and decay before any write.
- FastAPI `serve/` module exposes the candidate REST API (auth, store, pipeline adapter).
- `knowledge/evals/` contains YAML case definitions, `FakeRunner`, `ClaudeCodeRunner`, and deterministic structural checks.

### C. Capture, Eval & Infra (`session-capture/`, `infra/`, `knowledge/evals/`)
- Python capture layer (capture.py): subprocess wrapper for session JSONL logging, optional boto3 DynamoDB.
- Eval harness with FakeRunner + real ClaudeCodeRunner (--real, system prompt injection).
- Metrics endpoint and paired runs deliver compounding proof.

---

## 4. Technology Stack & Deployment Topology

- **Frontend:** React 19, Vite, TypeScript, Vitest, React Testing Library, Tailwind (implied modern UI).
- **Backend Contracts & KG:** Python 3.12+, uv, Pydantic, FastAPI, pytest, ruff, mypy.
- **Capture:** Python (subprocess + JSONL; Go/DynamoDB optional future).
- **Infra:** AWS CDK (DynamoDB), Render.com (recommended zero-config deploy via Dockerfile + render.yaml).
- **Local Dev:** Docker 24+, `uv sync --dev`, `npm install` in `frontend-react/`.
- **IDE / Agent Compatibility:** Strict typing, modular schemas, and docstrings optimized for Cursor, Claude, and automated agents via MCP-friendly patterns.
- **CI/CD:** `.gitlab-ci.yml` with SAST + secret detection (extend for full test/build/deploy gates).

**Local Portability:** Single `Dockerfile` + `render.yaml` for instant deploy; `uv run` or `docker compose` for local.

---

## 5. Security, Compliance & Failure Modes

- **Human-Gate Enforcement:** No graph mutation without explicit human decision; full decision provenance stored.
- **Contract Isolation:** Prevents accidental coupling; enables independent pillar evolution.
- **Stateless Sovereignty (where possible):** Session capture writes to DynamoDB; KG is in-memory for the lite scope (production would add persistent vector store).
- **Circuit Breaking & Resilience:** Dashboard gracefully degrades to mock data if candidate API is unavailable.
- **Eval Determinism:** All checks are replayable; no hidden randomness in promotion decisions.
- **Known Gaps (pre-demo):** Live candidate server not yet in-repo; root pytest requires `PYTHONPATH=frontend`; no full CI pipeline yet.

---

*This document is the canonical architecture reference. It supersedes all prior LLM-Shield or legacy diagrams. Last updated: 2026-06-21 (aligned to AUDIT.md and current pillar implementations).*