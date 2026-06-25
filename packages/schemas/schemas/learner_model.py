"""Adaptive learner model schemas — profiles, mastery, student model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LearnerProfileInput(BaseModel):
    """Onboarding payload for POST /v1/onboarding/submit."""

    goal: str = Field(min_length=1, max_length=500)
    grade_level: str | None = None
    points_group: str | None = None
    subjects: list[str] = Field(min_length=1)
    hours_per_week: float = Field(ge=1, le=40)
    preferred_style: str | None = None
    attention_span: int | None = Field(default=None, ge=10, le=180)
    self_scores: dict[str, int] = Field(default_factory=dict)
    background_notes: str | None = None


class AdaptiveLearnerProfile(BaseModel):
    """Persisted learner profile from onboarding."""

    learner_id: str
    goal: str
    grade_level: str | None = None
    points_group: str | None = None
    subjects: list[str]
    hours_per_week: float
    preferred_style: str | None = None
    attention_span: int | None = None
    self_scores: dict[str, int] | None = None
    background_notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StudentModel(BaseModel):
    """Aggregated view of what a learner knows."""

    learner_id: str
    profile: AdaptiveLearnerProfile | None = None
    mastery: dict[str, float] = Field(default_factory=dict)
    weak: list[str] = Field(default_factory=list)
    developing: list[str] = Field(default_factory=list)
    strong: list[str] = Field(default_factory=list)
    last_active: datetime | None = None


def self_score_to_mastery(score: int) -> float:
    """Map 1–10 self-rating to 0.1–0.9 mastery seed."""
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
