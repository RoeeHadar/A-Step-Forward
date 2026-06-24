"""Shared ingestion types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from schemas.common import Provenance


@dataclass
class RawDocument:
    id: str
    title: str
    text: str
    source: Provenance
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionResult:
    document_id: str
    chunks: int
    nodes_written: int
    edges_written: int
    pending_review: int
