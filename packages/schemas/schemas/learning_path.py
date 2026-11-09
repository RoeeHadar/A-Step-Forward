from __future__ import annotations

from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model


class PlanConcept(FlexibleModel):
    concept_id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    mastery: Any = None
    name: Any = None
    recommended_bagrut: Any = None
    subject: Any = None
    suggested_sections: Any = None


class PlanWeek(FlexibleModel):
    week_number: int = 1
    concepts: list[PlanConcept] = Field(default_factory=list)
    # AS-90: fields read in production (was model_extra fallback).
    content_ids: Any = None
    id: Any = None
    plan_id: Any = None
    quiz_due_at: Any = None
    status: Any = None


class LearningPlan(FlexibleModel):
    learner_id: str = ""
    weeks: list[PlanWeek] = Field(default_factory=list)
    # AS-90: fields read in production (was model_extra fallback).
    end_date: Any = None
    goal: Any = None
    id: Any = None
    start_date: Any = None
    status: Any = None


class QuizOption(FlexibleModel):
    id: str = ""
    text: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    key: Any = None


class StoredQuizItem(FlexibleModel):
    id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    correct: Any = None
    difficulty: Any = None
    options: Any = None
    source: str | None = None
    stem: Any = None
    subject: Any = None
    topic: Any = None


class QuizAnswerItem(FlexibleModel):
    question_id: str = ""
    answer: Any = None
    # AS-90: fields read in production (was model_extra fallback).
    chosen: Any = None
    item_id: Any = None


class QuizStartResponse(FlexibleModel):
    quiz_id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    plan_id: Any = None
    questions: Any = None
    started_at: Any = None
    time_limit_s: Any = None
    week_id: Any = None
    week_number: Any = None


class QuizSubmitResponse(FlexibleModel):
    score: float | None = None
    # AS-90: fields read in production (was model_extra fallback).
    next_week_concepts: Any = None
    per_topic: Any = None
    plan_adapted: Any = None
    quiz_id: Any = None
    weak_concepts: Any = None


class BagrutRef(FlexibleModel):
    id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    display_name: Any = None
    exam_type: Any = None
    file_url: Any = None
    year: Any = None


class ContentSectionRef(FlexibleModel):
    id: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    chunk_index: Any = None
    page_start: Any = None
    title: Any = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


class QuizQuestion(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    difficulty: Any = None
    id: Any = None
    options: Any = None
    stem: Any = None
    subject: Any = None
    topic: Any = None


class QuizSubmitRequest(FlexibleModel):
    """AS-90: declared (was flexible_model(); body.answers read in the quiz submit route)."""

    answers: Any = None


# ---------------------------------------------------------------------------
# AS-112: entry-point request models. The fields below were required before AS-90
# (3b7d2774 schemas); AS-90 declared them `= None` on the shared models, so an
# omitted field reached the service and crashed (500) instead of a 422. These
# subclasses are used only where untrusted input enters (FastAPI bodies, MCP tool
# signatures, LLM output); they restore the requirement without changing the
# shared models' defaults, the frozen AS90_DECLARED registry or any emitted
# output. Instances are still the base type, so services are unchanged.


class QuizAnswerBody(QuizAnswerItem):
    """One answer in the quiz submit body (pre-AS-90: item_id, chosen required)."""

    item_id: str
    chosen: str


class QuizSubmitBody(QuizSubmitRequest):
    """POST .../quiz/submit body. answers was `Any`, so items stayed raw dicts and the
    quiz repository's `a.item_id` reads failed; pre-AS-90: list[QuizAnswerItem]."""

    answers: list[QuizAnswerBody]
