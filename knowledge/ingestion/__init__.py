"""Ingestor ABC and variants (PromptIngestor default; JSONL, heuristic, distill planned)."""

from .parent_ingestor import Ingestor, Insight
from .ingestor_variants.prompt_ingestor import PromptIngestor

__all__ = ["Ingestor", "Insight", "PromptIngestor"]
