from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class LearnerProfileInput(FlexibleModel):
    learner_id: str | None = None


class StudentModel(FlexibleModel):
    learner_id: str = ""


class AdaptiveLearnerProfile(FlexibleModel):
    learner_id: str = ""


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
