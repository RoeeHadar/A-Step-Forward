"""Video transcript / plain-text source connector."""

from __future__ import annotations

from pathlib import Path

from schemas.common import Provenance

from ..types import RawDocument


def load_transcript(path: Path, *, doc_id: str) -> RawDocument:
    text = path.read_text(encoding="utf-8")
    return RawDocument(
        id=doc_id,
        title=path.stem.replace("-", " ").replace("_", " ").title(),
        text=text,
        source=Provenance(kind="import", id=doc_id),
        metadata={"format": path.suffix.lower().lstrip(".") or "txt", "path": str(path)},
    )
