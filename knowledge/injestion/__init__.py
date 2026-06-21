"""Ingestor ABC and variants (PromptIngestor default; JSONL, heuristic, distill planned)."""

from .parent_injestor import Ingestor, Insight
from .injestor_variants.prompt_injestor import PromptIngestor

__all__ = ["Ingestor", "Insight", "PromptIngestor"]
