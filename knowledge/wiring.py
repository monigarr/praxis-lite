"""build_trio() factory — wires Ingestor + Graph + Reader per substrate."""

from __future__ import annotations

from typing import Any

from knowledge.graph_reader.grapher_reader_variants.retrieving_reader import RetrievingReader
from knowledge.graph_reader.grapher_reader_variants.whole_file_reader import WholeFileReader
from knowledge.injestion.injestor_variants.prompt_injestor import PromptIngestor
from knowledge.knowledge_graph import InMemoryGraph, VectorGraph


def build_trio(substrate: str = "memory", dsn: str | None = None) -> dict[str, Any]:
    if substrate == "vector":
        graph = VectorGraph(dsn)
        reader = RetrievingReader(graph)
    elif substrate == "retrieving":
        graph = InMemoryGraph()
        reader = RetrievingReader(graph)
    else:
        graph = InMemoryGraph()
        reader = WholeFileReader(graph)
    ingestor = PromptIngestor()
    return {"graph": graph, "ingestor": ingestor, "reader": reader}
