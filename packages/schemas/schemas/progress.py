from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
