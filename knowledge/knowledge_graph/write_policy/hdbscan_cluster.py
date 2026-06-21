"""HDBSCAN clustering for dedup (sklearn fallback if hdbscan unavailable)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN


class HdbscanClusterer:
    def __init__(self, min_cluster_size: int = 2, metric: str = "cosine") -> None:
        self.min_cluster_size = min_cluster_size
        self.metric = metric

    def cluster(self, embeddings: list[list[float]]) -> list[int]:
        if not embeddings:
            return []
        X = np.array(embeddings)
        # Fallback to DBSCAN (HDBSCAN may not be installed everywhere)
        try:
            import hdbscan  # type: ignore

            clusterer = hdbscan.HDBSCAN(min_cluster_size=self.min_cluster_size, metric=self.metric)
            labels = clusterer.fit_predict(X)
        except Exception:
            clusterer = DBSCAN(eps=0.3, min_samples=self.min_cluster_size, metric=self.metric)
            labels = clusterer.fit_predict(X)
        return labels.tolist() if hasattr(labels, "tolist") else list(labels)
