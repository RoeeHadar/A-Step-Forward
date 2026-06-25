"""Learning path and weekly quiz schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class ContentSectionRef(BaseModel):
    id: str
    title: str
    chunk_index: int | None = None
    page_start: int | None = None


class BagrutRef(BaseModel):
    display_name: str
    file_url: str
    year: int | None = None
    exam_type: str | None = None


class PlanConcept(BaseModel):
    concept_id: str
    name: str
    subject: str
    mastery: float | None = None
    suggested_sections: list[ContentSectionRef] = Field(default_factory=list)
    recommended_bagrut: list[BagrutRef] = Field(default_factory=list)


class PlanWeek(BaseModel):
    id: str
    plan_id: str
    week_number: int
    concepts: list[PlanConcept] = Field(default_factory=list)
    content_ids: list[str] | None = None
    quiz_due_at: datetime | None = None
    status: str = "upcoming"


class LearningPlan(BaseModel):
    id: str
    learner_id: str
    goal: str
    start_date: date
    end_date: date | None = None
    status: str = "active"
    weeks: list[PlanWeek] = Field(default_factory=list)


class QuizOption(BaseModel):
    key: str
    text: str


class QuizQuestion(BaseModel):
    """Client-safe quiz item (no correct answer exposed)."""

    id: str
    topic: str
    subject: str
    difficulty: float
    stem: str
    options: list[QuizOption]


class StoredQuizItem(BaseModel):
    """Full quiz item persisted in weekly_quizzes.items JSONB."""

    id: str
    topic: str
    subject: str
    difficulty: float
    stem: str
    options: list[QuizOption]
    correct: str
    source: str = "bank"


class QuizStartResponse(BaseModel):
    quiz_id: str
    week_id: str
    plan_id: str
    week_number: int
    time_limit_s: int
    questions: list[QuizQuestion]
    started_at: datetime


class QuizAnswerItem(BaseModel):
    item_id: str
    chosen: str = Field(min_length=1, max_length=8)
    time_spent_s: int | None = Field(default=None, ge=0, le=3600)


class QuizSubmitRequest(BaseModel):
    answers: list[QuizAnswerItem] = Field(min_length=1)


class QuizSubmitResponse(BaseModel):
    quiz_id: str
    score: float
    per_topic: dict[str, float]
    weak_concepts: list[str]
    plan_adapted: bool = False
    next_week_concepts: list[str] | None = None
