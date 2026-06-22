"""build_trio() factory — wires Ingestor + Graph + Reader per substrate."""

from __future__ import annotations

from typing import Any

from knowledge.graph_reader.grapher_reader_variants.retrieving_reader import RetrievingReader
from knowledge.graph_reader.grapher_reader_variants.whole_file_reader import WholeFileReader
from knowledge.ingestion.ingestor_variants.heuristic_moment_ingestor import HeuristicLearningMomentIngestor
from knowledge.ingestion.ingestor_variants.jsonl_ingestor import JsonlIngestor
from knowledge.ingestion.ingestor_variants.prompt_ingestor import PromptIngestor
from knowledge.ingestion.ingestor_variants.structured_distill_ingestor import StructuredDistillIngestor
from knowledge.knowledge_graph import InMemoryGraph, VectorGraph


def build_trio(
    substrate: str = "memory", dsn: str | None = None, ingestor_type: str = "prompt"
) -> dict[str, Any]:
    if substrate == "vector":
        graph = VectorGraph(dsn)
        reader = RetrievingReader(graph)
    elif substrate == "retrieving":
        graph = InMemoryGraph()
        reader = RetrievingReader(graph)
    else:
        graph = InMemoryGraph()
        reader = WholeFileReader(graph)

    if ingestor_type == "jsonl":
        ingestor = JsonlIngestor()
    elif ingestor_type == "structured":
        ingestor = StructuredDistillIngestor()
    elif ingestor_type == "heuristic":
        ingestor = HeuristicLearningMomentIngestor()
    else:
        ingestor = PromptIngestor()

    return {"graph": graph, "ingestor": ingestor, "reader": reader}
