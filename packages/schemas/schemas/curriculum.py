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


class CourseSummary(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    id: Any = None
    lesson_count: Any = None
    level: Any = None
    summary: Any = None
    title: Any = None
    unit_count: Any = None


class LearningPathSuggestion(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    goal_id: Any = None
    learner_id: Any = None
    steps: Any = None


class LessonMatch(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    course_id: Any = None
    lesson: Any = None
    matched_concepts: list[Any] | None = None
    unit_id: Any = None


class PathStep(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    est_minutes: Any = None
    lesson_id: Any = None
    reason: Any = None
    title: Any = None
