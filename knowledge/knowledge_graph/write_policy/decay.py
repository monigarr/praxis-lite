"""Decay policy: active → decayed after threshold days or low confidence."""

from datetime import datetime, timedelta
from typing import Any


class DecayPolicy:
    def __init__(self, max_age_days: int = 90, min_confidence: float = 0.3) -> None:
        self.max_age_days = max_age_days
        self.min_confidence = min_confidence

    def should_decay(self, fact: dict[str, Any]) -> bool:
        ts = fact.get("updated_at") or fact.get("created_at")
        if ts:
            try:
                dt = datetime.fromisoformat(str(ts).replace("Z", ""))
                if (datetime.utcnow() - dt).days > self.max_age_days:
                    return True
            except Exception:
                pass
        return fact.get("confidence", 1.0) < self.min_confidence
