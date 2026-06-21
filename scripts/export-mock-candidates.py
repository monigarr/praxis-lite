"""Export Python mock_data to frontend-react/public/mock-candidates.json.

Run this whenever seed data changes so the React dashboard stays in sync.
"""

from __future__ import annotations

import json
from pathlib import Path

from frontend.mock_data import SEED_CANDIDATES


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "frontend-react" / "public"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = [c.to_dict() for c in SEED_CANDIDATES]
    (out_dir / "mock-candidates.json").write_text(json.dumps(payload, indent=2))
    print(f"Exported {len(payload)} candidates to {out_dir / 'mock-candidates.json'}")


if __name__ == "__main__":
    main()
