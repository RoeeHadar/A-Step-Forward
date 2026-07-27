from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model


class SeedBundle(FlexibleModel):
    courses: list[Any] = Field(default_factory=list)


def load_seed_course(path: str | Path | None = None) -> SeedBundle:
    return SeedBundle(source=str(path) if path is not None else None)


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
