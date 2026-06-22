# Product Requirements Document (PRD)

## Project: PRAXIS Lite
### Document Version: 1.0.0 (Capstone Sprint)
### Target Audience: Gauntlet AI Capstone Reviewers & Stakeholders
### Sprint: June 2026 (Days 1–10)

---

## 1. Executive Summary & Problem Statement

Claude Code agents operating in the Gauntlet ecosystem produce rich session data but lack a persistent, self-improving organizational memory. Every session starts from a blank slate; valuable patterns, decisions, and learnings evaporate at context-window boundaries. Teams need a governed pipeline that captures sessions, distills them into a living knowledge graph (KG), proposes candidates for promotion, and requires explicit human review before any knowledge enters the canonical store.

**PRAXIS Lite** (Prompt-Response Agent eXperience Improvement System) delivers a three-pillar, contract-driven reference implementation that closes this loop:

- Captures Claude Code sessions via PTY wrapper + DynamoDB persistence
- Ingests, clusters, scores, and deduplicates learning moments into an in-memory + vector KG
- Exposes candidate proposals through a versioned REST API
- Provides a React + Vite Human Gate Dashboard for review, promotion, contradiction, and decay decisions

The system enforces strict provenance, contradiction detection, deterministic eval harnesses, and a "no-cross-import" boundary between the dashboard contract layer and the knowledge pipeline.

---

## 2. Strategic Objectives (Three-Pillar Model)

PRAXIS is organized around three independent pillars with clear ownership and integration contracts:

1. **Dashboard & Human Gate (Monica Peters)** — High-maturity React 19 + Vite dashboard with Python contract layer. Enables human-in-the-loop governance (`proposed → suggested → active → decayed` state machine, provenance tracking, contradiction workflows).

2. **ML & Knowledge Pipeline (Matthew Daw)** — Core KG (InMemoryGraph + vector), ingestion pipeline, write policies (cluster/dedupe/conflict/score/decay), and FastAPI candidate service.

3. **Architecture, Eval & Integration (Dominic Antonelli)** — YAML-driven eval harness, deterministic checks, Go `claude+` session capture to DynamoDB, AWS CDK infra, and integration smoke tests.

**Integration contracts (v1)** are the source of truth (see `docs/integration/candidate-api-v1.md`, `docs/integration/eval-metrics-v1.md`).

---

## 3. Scope & Target Constraints

- **Human Oversight First:** No candidate enters the canonical KG without explicit human gate action. Full audit trail of every promotion/contradiction/decay decision.
- **Provenance & Reproducibility:** Every candidate carries required provenance metadata; all eval runs are deterministic and replayable.
- **Contract Isolation:** `frontend/` and `frontend-react/` never import from `knowledge/`; all interaction occurs via documented REST contracts or mock fixtures.
- **Ephemeral & Portable:** Zero-config local run via Docker or `uv run`; deployable to Render.com; optional AWS CDK for sessions table.
- **Demo-Ready on Mocks:** Human-gate pillar is fully functional against mock data and contract tests for Days 6–7 integration; live candidate API is the critical path for full end-to-end.

**Out of Scope (this sprint):** Production-grade persistent vector DB, multi-tenant auth, real-time collaboration, non-Claude agent support.

---

## 4. Core Functional Features

- **Session Capture & Persistence:** Shipped Go `claude+` daemon ([`session-capture/`](session-capture/)) — cross-platform PTY (POSIX + Windows ConPTY), fsnotify JSONL tailer, monotonic-seq event emitter, local rolling JSONL `FileSink` (always on) + best-effort `DynamoDBSink` (opt-in via `PRAXIS_SESSIONS_TABLE`), CDK `PraxisSessionsTableStack` in [`infra/`](infra/).
- **Knowledge Graph & Ingestion:** InMemoryGraph + vector store, prompt/JSONL/heuristic ingestors, clustering, deduplication, conflict detection, scoring, and decay policies.
- **Candidate API (v1):** `GET/POST /candidates/*` contract for proposing, listing, and promoting candidates (FastAPI in `knowledge/serve/`).
- **Human Gate Dashboard (React 19 + Vite):** Interactive review UI supporting promote, contradict (pairwise), decay, and state-machine visualization. Toggle between mock and live API modes.
- **Eval Harness & Metrics:** YAML case definitions, FakeRunner + ClaudeCodeRunner, deterministic structural checks, compounding metrics endpoint.
- **Contract Testing:** 11+ pytest tests validating state machine, provenance, mock fixtures, and API client retry logic (`PYTHONPATH=frontend`).
- **Observability & Compliance:** Structured logging, provenance on all candidates, contradiction pair tracking, Section-508-friendly UI patterns.

---

## 5. Non-Functional & Operational Requirements

- **Performance:** Dashboard remains responsive on 1000+ candidates; ingestion handles typical Gauntlet session volume without blocking.
- **Stability:** Failures in one pillar (e.g., candidate API down) do not crash the dashboard; graceful degradation to mock mode.
- **Zero-Trust Boundaries:** Strict no-cross-import rule; all inter-pillar communication via contracts or explicit fixtures.
- **Test Posture:** All contract tests pass; eval harness deterministic; no root `pytest` failures once `PYTHONPATH=frontend` documented.
- **CI Readiness:** `.gitlab-ci.yml` present with SAST/secret detection; full pipeline (test, build, deploy) is a known gap for Days 9–10.
- **Deployment:** Single Dockerfile + render.yaml for zero-config deploy; optional CDK for DynamoDB.

---

## 6. Risks & Open Items (Pre-Demo)

1. Live candidate REST server (`knowledge/serve/`) is critical path for full integration.
2. Root `pytest` requires `PYTHONPATH=frontend` (undocumented in `pyproject.toml`).
3. No automated CI gate — regressions currently rely on manual runs.
4. Eval compounding proof depends on metrics endpoint + real replay runs (Dominic).

---

*Document maintained in sync with AUDIT.md, README.md, and pillar owners. Last updated: 2026-06-21.*