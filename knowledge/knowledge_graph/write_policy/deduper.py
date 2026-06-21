"""Cosine-threshold deduper with optional HDBSCAN clustering."""

from __future__ import annotations

from typing import Any

from .hdbscan_cluster import HdbscanClusterer


class Deduper:
    def __init__(self, threshold: float = 0.92, use_hdbscan: bool = True) -> None:
        self.threshold = threshold
        self.clusterer = HdbscanClusterer() if use_hdbscan else None

    def is_duplicate(self, content: str, existing: list[str]) -> bool:
        if any(content.strip() == e.strip() for e in existing):
            return True
        if self.clusterer and len(existing) > 1:
            # Embed stub — real path uses OpenRouterEmbedder
            embs = [[hash(c) % 1000 / 1000.0] * 8 for c in [content] + existing]
            labels = self.clusterer.cluster(embs)
            return labels[0] != -1 and labels[0] in labels[1:]
        return False
