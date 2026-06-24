"""Chunker unit tests."""

from __future__ import annotations

from graphrag_service.ingest.chunker import SemanticChunker
from graphrag_service.settings import GraphRAGSettings


def test_semantic_chunker_respects_headings() -> None:
    text = "# Fractions\n\nFractions are parts of a whole.\n\n# Division\n\nDivision splits quantities."
    chunker = SemanticChunker(GraphRAGSettings(chunk_tokens=40, chunk_overlap=5))
    chunks = chunker.split(text)
    assert chunks
    assert any(c.heading == "Fractions" for c in chunks)
    assert all(c.token_count > 0 for c in chunks)
