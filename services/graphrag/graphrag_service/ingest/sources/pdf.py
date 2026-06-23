"""PDF source connector (text extraction only; no OCR)."""

from __future__ import annotations

from pathlib import Path

from schemas.common import Provenance

from ..types import RawDocument


def load_pdf(path: Path, *, doc_id: str) -> RawDocument:
    try:
        from pypdf import PdfReader  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("Install pypdf to ingest PDF documents") from exc

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages).strip()
    return RawDocument(
        id=doc_id,
        title=path.stem.replace("-", " ").replace("_", " ").title(),
        text=text,
        source=Provenance(kind="import", id=doc_id),
        metadata={"format": "pdf", "path": str(path), "pages": len(pages)},
    )
