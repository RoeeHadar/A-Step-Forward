from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class Provenance(FlexibleModel):
    source: str | None = None
    agent: str | None = None
    timestamp: str | None = None


class Citation(FlexibleModel):
    title: str | None = None
    url: str | None = None
    agent: str | None = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
