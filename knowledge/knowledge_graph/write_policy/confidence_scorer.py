"""Frequency / recency / breadth confidence scorer."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


class ConfidenceScorer:
    def score(self, facts: list[dict[str, Any]], window_days: int = 30) -> dict[str, float]:
        if not facts:
            return {"frequency": 0.0, "recency": 0.0, "breadth": 0.0}
        now = datetime.utcnow()
        freq = min(1.0, len(facts) / 10.0)
        recencies = []
        for f in facts:
            ts = f.get("created_at") or f.get("createdAt")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", ""))
                    age = (now - dt).days
                    recencies.append(max(0.0, 1.0 - age / window_days))
                except Exception:
                    recencies.append(0.5)
        recency = sum(recencies) / len(recencies) if recencies else 0.5
        breadth = min(1.0, len(set(f.get("scope", "general") for f in facts)) / 5.0)
        return {"frequency": round(freq, 2), "recency": round(recency, 2), "breadth": round(breadth, 2)}
