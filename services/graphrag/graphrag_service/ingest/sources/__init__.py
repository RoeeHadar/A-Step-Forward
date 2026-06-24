"""Source connectors for GraphRAG ingestion."""

from __future__ import annotations

from pathlib import Path

from ..types import RawDocument
from .html import load_html
from .markdown import load_markdown
from .pdf import load_pdf
from .transcript import load_transcript

__all__ = ["load_document"]


def load_document(path: Path, *, doc_id: str | None = None) -> RawDocument:
    """Load a supported document format into a RawDocument."""
    suffix = path.suffix.lower()
    doc_id = doc_id or path.stem
    if suffix in {".md", ".markdown"}:
        return load_markdown(path, doc_id=doc_id)
    if suffix in {".html", ".htm"}:
        return load_html(path, doc_id=doc_id)
    if suffix == ".pdf":
        return load_pdf(path, doc_id=doc_id)
    if suffix in {".txt", ".vtt", ".srt"}:
        return load_transcript(path, doc_id=doc_id)
    raise ValueError(f"Unsupported document type: {suffix}")
