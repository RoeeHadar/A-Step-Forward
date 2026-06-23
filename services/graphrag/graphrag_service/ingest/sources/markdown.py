"""Markdown source connector."""

from __future__ import annotations

from pathlib import Path

from schemas.common import Provenance

from ..types import RawDocument


def load_markdown(path: Path, *, doc_id: str) -> RawDocument:
    text = path.read_text(encoding="utf-8")
    title = path.stem.replace("-", " ").replace("_", " ").title()
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return RawDocument(
        id=doc_id,
        title=title,
        text=text,
        source=Provenance(kind="import", id=doc_id),
        metadata={"format": "markdown", "path": str(path)},
    )
