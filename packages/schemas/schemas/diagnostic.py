from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class DiagnosticOption(FlexibleModel):
    id: str = ""
    text: str = ""


class DiagnosticQuestion(FlexibleModel):
    id: str = ""
    prompt: str = ""


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
