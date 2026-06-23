"""Progress and mastery schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .common import ConfidenceScore, IDStr


class MasteryEntry(BaseModel):
    concept_id: IDStr
    concept_title: str
    score: ConfidenceScore
    last_reviewed_at: datetime | None = None


class ProgressSummary(BaseModel):
    """Current mastery summary returned by GET /v1/progress."""

    learner_id: IDStr
    mastery: list[MasteryEntry] = Field(default_factory=list)
    streak_days: int = 0
    next_review_at: datetime | None = None


# ---------- MCP tool inputs / outputs ----------


class LearnerRefInput(BaseModel):
    learner_id: IDStr


class UpdateMasteryInput(BaseModel):
    learner_id: IDStr
    concept_id: IDStr
    score: ConfidenceScore


class KnowledgeGaps(BaseModel):
    learner_id: IDStr
    gaps: list[MasteryEntry] = Field(default_factory=list)


class StreakInfo(BaseModel):
    learner_id: IDStr
    streak_days: int = 0
    next_review_at: datetime | None = None


class UpdateMasteryResult(BaseModel):
    updated: bool = True
    entry: MasteryEntry | None = None
