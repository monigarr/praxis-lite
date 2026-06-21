# Matthew Handoff — P0 Eval Cases Acknowledged

**Owner:** Matthew Daw (ML Pipeline)  
**Date:** 2026-06-21

## Acknowledged P0 cases (quirky_*)

- `quirky_exhaustive_switch` — TypeScript discriminated union exhaustive check.  
  Pipeline must surface this as candidate with provenance from JSONL.

- `quirky_config_load_order` — Config precedence bug (env vs file).  
  Must be distilled with correct `when` / `scope` metadata.

These cases are covered by the `JsonlIngestor` + `HeuristicLearningMomentIngestor` + `StructuredDistillIngestor` variants and the promote → `KnowledgeGraph.write` path.

The `build_trio()` factory and candidate API now support end-to-end flow for these cases.

**Next:** Dominic to wire cold-vs-injected runner using `RetrievingReader`.
