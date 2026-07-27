from __future__ import annotations

from enum import StrEnum
from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class LearnerRole(StrEnum):
    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"


class LearnerProfile(FlexibleModel):
    learner_id: str = ""
    role: LearnerRole | str = LearnerRole.STUDENT


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
