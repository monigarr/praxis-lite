"""Contradiction detection (LLM-assisted)."""

from typing import Any

from knowledge.llm.openrouter import OpenRouterLlm


class ConflictFlagger:
    def __init__(self, llm: OpenRouterLlm | None = None) -> None:
        self.llm = llm or OpenRouterLlm()

    def find_conflicts(self, new_fact: dict[str, Any], graph_facts: list[dict[str, Any]]) -> list[str]:
        if not graph_facts:
            return []
        prompt = (
            "Given a new fact and existing facts, return IDs of any that contradict the new fact.\n"
            f"NEW: {new_fact}\nEXISTING: {graph_facts[:5]}\nReturn JSON list of conflicting IDs or []."
        )
        raw = self.llm.complete(prompt)
        try:
            import json
            import re

            m = re.search(r"\[.*\]", raw, re.S)
            if m:
                ids = json.loads(m.group(0))
                return [str(i) for i in ids]
        except Exception:
            pass
        return []
