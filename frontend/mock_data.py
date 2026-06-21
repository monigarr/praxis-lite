"""Seed data for the mock provider and React export script.

These fixtures are the source of truth for offline demo and contract tests.
They deliberately include the cand_9 ↔ cand_16 contradiction pair used in Act 2.
"""

from __future__ import annotations

from .models.candidate import Candidate

SEED_CANDIDATES: list[Candidate] = [
    Candidate.from_mapping(
        {
            "id": "cand_1",
            "title": "TypeScript Exhaustive Switch Pattern",
            "content": "When using a switch statement on a discriminated union or enum, include a default case that assigns the value to a variable of type `never`.",
            "state": "proposed",
            "confidence": 0.85,
            "provenance": "logs/session_20260615.jsonl:88",
            "createdAt": "2026-06-15T14:30:00Z",
            "confidenceBreakdown": {"frequency": 0.82, "recency": 0.88, "breadth": 0.76},
        }
    ),
    Candidate.from_mapping(
        {
            "id": "cand_2",
            "title": "React useEffect Cleanup",
            "content": "Always return a cleanup function from useEffect when subscribing to external events or setting up intervals.",
            "state": "suggested",
            "confidence": 0.92,
            "provenance": "logs/session_20260614.jsonl:214",
            "createdAt": "2026-06-14T09:15:00Z",
        }
    ),
    Candidate.from_mapping(
        {
            "id": "cand_9",
            "title": "Prefer explicit error types in Rust",
            "content": "Use custom error enums instead of Box<dyn Error> in library code for clearer propagation.",
            "state": "suggested",
            "confidence": 0.71,
            "provenance": "logs/session_20260612.jsonl:301",
            "createdAt": "2026-06-12T08:00:00Z",
            "contradictions": ["cand_16"],
        }
    ),
    Candidate.from_mapping(
        {
            "id": "cand_16",
            "title": "Use anyhow::Error for application errors",
            "content": "For application binaries, anyhow::Error + thiserror is the pragmatic choice; reserve custom enums for library crates.",
            "state": "suggested",
            "confidence": 0.68,
            "provenance": "logs/session_20260612.jsonl:312",
            "createdAt": "2026-06-12T08:05:00Z",
            "contradictions": ["cand_9"],
        }
    ),
    Candidate.from_mapping(
        {
            "id": "cand_12",
            "title": "Python pathlib preference",
            "content": "Prefer pathlib.Path over os.path for all new filesystem code.",
            "state": "active",
            "confidence": 0.95,
            "provenance": "logs/session_20260610.jsonl:45",
            "createdAt": "2026-06-10T10:00:00Z",
        }
    ),
    Candidate.from_mapping(
        {
            "id": "cand_18",
            "title": "Docstring policy for public APIs",
            "content": "All public functions must have Google-style docstrings with Args, Returns, Raises.",
            "state": "decayed",
            "confidence": 0.40,
            "provenance": "logs/session_20260609.jsonl:77",
            "createdAt": "2026-06-09T16:20:00Z",
        }
    ),
]

# Additional candidates to reach the documented 17+ count for export
for i in range(3, 9):
    SEED_CANDIDATES.append(
        Candidate.from_mapping(
            {
                "id": f"cand_{i}",
                "title": f"Lesson {i}",
                "content": f"Auto-generated lesson content {i}.",
                "state": "proposed" if i % 2 == 0 else "suggested",
                "confidence": 0.6 + (i % 5) * 0.05,
                "provenance": f"logs/session_2026061{i}.jsonl:{i*10}",
                "createdAt": f"2026-06-1{i}T12:00:00Z",
            }
        )
    )

for i in range(10, 15):
    SEED_CANDIDATES.append(
        Candidate.from_mapping(
            {
                "id": f"cand_{i}",
                "title": f"Lesson {i}",
                "content": f"Auto-generated lesson content {i}.",
                "state": "active",
                "confidence": 0.8,
                "provenance": f"logs/session_2026061{i}.jsonl:{i*7}",
                "createdAt": f"2026-06-1{i}T09:00:00Z",
            }
        )
    )
