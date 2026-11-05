from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class LearnerProfileInput(FlexibleModel):
    learner_id: str | None = None
    # AS-90: fields read in production (was model_extra fallback).
    attention_span: Any = None
    background_notes: Any = None
    goal: Any = None
    grade_level: Any = None
    hours_per_week: Any = None
    points_group: Any = None
    preferred_style: Any = None
    self_scores: Any = None
    subjects: Any = None


class StudentModel(FlexibleModel):
    learner_id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    developing: Any = None
    last_active: Any = None
    mastery: Any = None
    profile: Any = None
    strong: Any = None
    weak: Any = None


class AdaptiveLearnerProfile(FlexibleModel):
    learner_id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    attention_span: Any = None
    background_notes: Any = None
    created_at: Any = None
    goal: Any = None
    grade_level: Any = None
    hours_per_week: Any = None
    points_group: Any = None
    preferred_style: Any = None
    self_scores: Any = None
    subjects: Any = None
    updated_at: Any = None


# AS-89: restored from bbd20c4 (lost in the ed6747a schemas rewrite). Without them the
# module __getattr__ below turns these names into dynamic model classes, so every
# call raised "BaseModel.__init__() takes 1 positional argument" once AS-88 r1 let
# create_profile / get_student_model get this far.
def self_score_to_mastery(score: int) -> float:
    """Map 1-10 self-rating to 0.1-0.9 mastery seed."""
    clamped = max(1, min(10, score))
    return round(0.1 + (clamped - 1) * (0.8 / 9), 4)


def classify_mastery(mastery: dict[str, float]) -> tuple[list[str], list[str], list[str]]:
    """Return (weak, developing, strong) concept id lists."""
    weak: list[str] = []
    developing: list[str] = []
    strong: list[str] = []
    for concept_id, score in mastery.items():
        if score < 0.4:
            weak.append(concept_id)
        elif score <= 0.7:
            developing.append(concept_id)
        else:
            strong.append(concept_id)
    return weak, developing, strong


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
