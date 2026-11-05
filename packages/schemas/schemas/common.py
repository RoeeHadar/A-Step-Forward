from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class Provenance(FlexibleModel):
    kind: str | None = None
    source: str | None = None
    agent: str | None = None
    timestamp: str | None = None
    # AS-90: fields read in production (was model_extra fallback).
    id: Any = None
    model: str | None = None


class Citation(FlexibleModel):
    title: str | None = None
    url: str | None = None
    agent: str | None = None
    # AS-90: fields read in production (was model_extra fallback).
    quote: str | None = None
    score: float | None = None
    source_id: str | None = None
    source_kind: str | None = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
