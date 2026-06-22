# Dominic — 3-Act Spoken Demo Script (≤10 min total)

**Lite version context:** This repo is the **praxis-lite** implementation Monica builds in parallel with the full system. Monica serves as Daily Scrum Master (10:00 AM syncs). See [docs/plans/PRAXIS_Project_Plan.html](../plans/PRAXIS_Project_Plan.html) for the locked architecture, Lite framing, and **🎯 Capstone Alignment (PRD)** box.

**Target:** 2.5 min Act 1 · 3.5 min Act 2 · 3.5 min Act 3 + close

---

## Act 1 — The Dumb Agent (2.5 min)

**Visual:** Terminal running `python -m knowledge.evals.demo.act_runner` with `quirky_exhaustive_switch` and `quirky_config_load_order` in cold mode.

**Spoken:**

> "Meet the cold agent. No memory, no context, just raw Claude Code.  
> Watch it fail the same quirky rule twice: exhaustive switch without a never-check, and config load order that prefers files over env vars.  
> Each failure costs a correction. In our benchmark, cold runs average 12 corrections across 4 tasks."

**Action:** Run cold, show correction counts on screen.

---

## Act 2 — Distillation & Human Gate (3.5 min)

**Visual:** Monica's React dashboard (Act 2) or mock if live API not ready.

**Spoken:**

> "Session logs stream to DynamoDB. Our pipeline detects learning moments, distills candidates, and surfaces them for human review.  
> Monica's gate enforces quality: only high-confidence, non-contradictory lessons get promoted.  
> Provenance is always visible — every lesson traces back to the exact JSONL line."

**Action:** Show 1-2 candidates, promote one, narrate the state machine (proposed → suggested → active).

---

## Act 3 — The Smart Agent + Scoreboard (3.5 min)

**Visual:** Same quirky cases now run with injected insight; dashboard embed shows `GET /metrics` curve.

**Spoken:**

> "Now the agent has context. Same tasks, same quirky repo.  
> Watch the correction count drop from 12 to 5 — a 58% reduction.  
> The compounding curve on the right shows the trajectory: each promoted lesson compounds.  
> This is the measurable proof that PRAXIS turns one-off mistakes into durable, queryable knowledge."

**Action:** Run injected, show metrics endpoint response, point to the line chart in the dashboard embed.

---

## Beat 4 — GitHub Hook & PR Recreation (1 min)

**Visual:** Terminal showing `python -m knowledge.evals.github_hook` or POST to `/ingest/github` with the `github_pr_event.json` fixture.

**Spoken:**
> "Learning moments often arrive via PRs or tickets. Dominic's GitHub hook ingests a simulated PR payload, extracts the quirk, and creates a candidate with full provenance.  
> The new eval case `quirky_pr_exhaustive_switch` replays the exact diff from the PR fixture."

**Action:** Call the ingest/github route or run the hook module; show the created candidate and the new case in the registry.

---

## Close (0.5 min)

> "Dominic's pillar turns the interview claim into reality: the eval harness and integration layer rigorously prove PRAXIS delivers ≥50% fewer corrections with compounding gains.  
> Questions?"
