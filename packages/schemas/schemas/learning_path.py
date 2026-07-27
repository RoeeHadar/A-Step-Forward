from __future__ import annotations

from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model


class PlanConcept(FlexibleModel):
    concept_id: str = ""


class PlanWeek(FlexibleModel):
    week_number: int = 1
    concepts: list[PlanConcept] = Field(default_factory=list)


class LearningPlan(FlexibleModel):
    learner_id: str = ""
    weeks: list[PlanWeek] = Field(default_factory=list)


class QuizOption(FlexibleModel):
    id: str = ""
    text: str = ""


class StoredQuizItem(FlexibleModel):
    id: str = ""


class QuizAnswerItem(FlexibleModel):
    question_id: str = ""
    answer: Any = None


class QuizStartResponse(FlexibleModel):
    quiz_id: str = ""


class QuizSubmitResponse(FlexibleModel):
    score: float | None = None


class BagrutRef(FlexibleModel):
    id: str = ""


class ContentSectionRef(FlexibleModel):
    id: str = ""


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
