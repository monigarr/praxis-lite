from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).parent.parent.parent / "docs" / "integration" / "fixtures"

def generate_pr_event(case_id: str, quirk: str, diff: str) -> dict[str, Any]:
    return {
        "action": "opened",
        "pull_request": {
            "id": 123456,
            "title": f"Fix {case_id}",
            "body": f"Addresses quirk: {quirk}",
            "diff_url": "https://example.com/diff",
            "head": {"ref": "fix/quirk"},
            "base": {"ref": "main"},
        },
        "quirk": quirk,
        "diff": diff,
    }

def generate_ticket(case_id: str, quirk: str) -> dict[str, Any]:
    return {
        "id": f"TICKET-{case_id.upper()}",
        "title": f"Handle {case_id}",
        "description": f"Agent must learn: {quirk}",
        "labels": ["quirky", "eval"],
    }

def extract_seed_prompt(payload: dict[str, Any]) -> str:
    if "quirk" in payload:
        return f"Implement handling for: {payload['quirk']}"
    if "pull_request" in payload:
        return payload["pull_request"].get("body", "")
    return ""

def extract_seeded_insight(payload: dict[str, Any]) -> str | None:
    return payload.get("quirk") or payload.get("diff")

def load_fixture(name: str) -> dict[str, Any]:
    p = FIXTURES_DIR / name
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", action="store_true")
    parser.add_argument("--ticket", action="store_true")
    args = parser.parse_args()

    if args.pr:
        ev = generate_pr_event("quirky_exhaustive_switch", "exhaustive union", "diff here")
        print(json.dumps(ev, indent=2))
    elif args.ticket:
        tk = generate_ticket("quirky_exhaustive_switch", "exhaustive union")
        print(json.dumps(tk, indent=2))
    else:
        print("Use --pr or --ticket")
