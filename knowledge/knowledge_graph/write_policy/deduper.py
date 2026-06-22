"""Cosine-threshold deduper with optional HDBSCAN clustering."""

from __future__ import annotations

from typing import Any

import numpy as np

from knowledge.llm.openrouter import OpenRouterEmbedder

from .hdbscan_cluster import HdbscanClusterer


class Deduper:
    def __init__(self, threshold: float = 0.92, use_hdbscan: bool = True, embedder: OpenRouterEmbedder | None = None) -> None:
        self.threshold = threshold
        self.clusterer = HdbscanClusterer() if use_hdbscan else None
        self.embedder = embedder or OpenRouterEmbedder()

    def _embed(self, text: str) -> list[float]:
        v = self.embedder.embed(text)
        if sum(v) == 0:
            v = np.random.default_rng(abs(hash(text)) % (2**32)).standard_normal(1536).astype(float).tolist()
        return v

    def is_duplicate(self, content: str, existing: list[str]) -> bool:
        if any(content.strip() == e.strip() for e in existing):
            return True
        if self.clusterer and len(existing) > 1:
            texts = [content] + existing
            embs = [self._embed(t) for t in texts]
            labels = self.clusterer.cluster(embs)
            return labels[0] != -1 and labels[0] in labels[1:]
        # cosine fallback
        if existing:
            qv = np.array(self._embed(content))
            for e in existing:
                ev = np.array(self._embed(e))
                sim = float(np.dot(qv, ev) / (np.linalg.norm(qv) * np.linalg.norm(ev) + 1e-9))
                if sim >= self.threshold:
                    return True
        return False
