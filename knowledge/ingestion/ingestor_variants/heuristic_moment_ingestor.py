"""HeuristicLearningMomentIngestor: detects failure→fix, correction patterns."""

from __future__ import annotations

import re
from typing import Any, Iterable
from uuid import uuid4

from knowledge.ingestion.parent_ingestor import Ingestor, Insight


class HeuristicLearningMomentIngestor(Ingestor):
    PATTERN = re.compile(r"(?i)(error|fail|bug|fix|should|must|always|never)")

    def ingest(self, source: str | Iterable[str], **kwargs: Any) -> list[Insight]:
        texts = [source] if isinstance(source, str) else list(source)
        insights: list[Insight] = []
        for t in texts:
            if self.PATTERN.search(t):
                insights.append(
                    Insight(
                        id=str(uuid4()),
                        title=t[:60],
                        content=t,
                        provenance=kwargs.get("provenance", "heuristic"),
                        scope="episode",
                    )
                )
        return insights
