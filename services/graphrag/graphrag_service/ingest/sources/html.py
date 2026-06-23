"""HTML source connector."""

from __future__ import annotations

import re
from html import unescape
from pathlib import Path

from schemas.common import Provenance

from ..types import RawDocument

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def load_html(path: Path, *, doc_id: str) -> RawDocument:
    raw = path.read_text(encoding="utf-8")
    title_match = re.search(r"<title>(.*?)</title>", raw, flags=re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else path.stem
    return RawDocument(
        id=doc_id,
        title=title,
        text=_strip_html(raw),
        source=Provenance(kind="import", id=doc_id),
        metadata={"format": "html", "path": str(path)},
    )
