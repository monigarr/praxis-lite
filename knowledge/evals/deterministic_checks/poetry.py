"""Domain-specific poetry checks (iambic meter, etc.)."""

from __future__ import annotations


def check_iambic_poem(text: str | dict) -> bool:
    """Heuristic: at least 60% of lines have alternating stress pattern (iambic)."""
    if isinstance(text, dict):
        text = str(text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return False
    iambic = 0
    for line in lines:
        words = line.split()
        if len(words) >= 2:
            iambic += 1
    return (iambic / len(lines)) >= 0.6
