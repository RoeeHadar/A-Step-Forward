from __future__ import annotations

from enum import StrEnum
from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class BloomsLevel(StrEnum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class Modality(StrEnum):
    TEXT = "text"
    VIDEO = "video"
    INTERACTIVE = "interactive"
    PRACTICE = "practice"


class Objective(FlexibleModel):
    id: str = ""
    description: str = ""


class Lesson(FlexibleModel):
    id: str = ""
    title: str = ""


class Course(FlexibleModel):
    id: str = ""
    title: str = ""


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
