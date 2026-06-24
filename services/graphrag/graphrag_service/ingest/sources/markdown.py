"""Markdown source connector."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from schemas.common import Provenance

from ..types import RawDocument

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(raw: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(raw)
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError:
        return {}


def load_markdown(path: Path, *, doc_id: str) -> RawDocument:
    full_text = path.read_text(encoding="utf-8")
    metadata: dict[str, Any] = {"format": "markdown", "path": str(path)}
    text = full_text

    match = _FRONTMATTER_RE.match(full_text)
    if match:
        fm = _parse_frontmatter(match.group(1))
        metadata.update(fm)
        text = full_text[match.end() :]
        if fm.get("id"):
            doc_id = str(fm["id"])

    title = path.stem.replace("-", " ").replace("_", " ").title()
    if metadata.get("title"):
        title = str(metadata["title"])
    else:
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break

    return RawDocument(
        id=doc_id,
        title=title,
        text=text.strip(),
        source=Provenance(kind="import", id=doc_id),
        metadata=metadata,
    )
