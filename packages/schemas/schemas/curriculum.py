from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model
from .common import IDStr


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


# ---------------------------------------------------------------------------
# AS-119: entry-point request models for the remaining pre-AS-90 bounds (3b7d2774).
# Same pattern as AS-112/113: these subclasses are used only where untrusted input
# enters (FastAPI bodies, MCP tool signatures, LLM output). The shared models, their
# defaults and the frozen AS90_DECLARED registry stay unchanged. Instances are still
# the base type, so the services are unchanged.


class CurriculumLevel(StrEnum):
    """The ref Level enum (3b7d2774 curriculum.py:11-14), for the list_courses input
    only. The name Level itself stays the AS-90 dynamic model."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CurriculumListCoursesBody(__getattr__("CurriculumListCoursesInput")):
    """curriculum.list_courses MCP input (3b7d2774 curriculum.py:194-196). level is the
    ref enum again, so the repository's level.value filter works as on the ref."""

    level: CurriculumLevel | None = None
    limit: int = Field(default=50, ge=1, le=200)


class CurriculumGetCourseBody(__getattr__("CurriculumGetCourseInput")):
    """curriculum.get_course MCP input (3b7d2774 curriculum.py:199-200)."""

    course_id: IDStr


class CurriculumGetLessonBody(__getattr__("CurriculumGetLessonInput")):
    """curriculum.get_lesson MCP input (3b7d2774 curriculum.py:203-204)."""

    lesson_id: IDStr


class CurriculumFindForConceptBody(__getattr__("CurriculumFindForConceptInput")):
    """curriculum.find_for_concept MCP input (3b7d2774 curriculum.py:207-209)."""

    concept_id: IDStr
    limit: int = Field(default=20, ge=1, le=100)


class CurriculumSuggestPathBody(__getattr__("CurriculumSuggestPathInput")):
    """curriculum.suggest_path MCP input (3b7d2774 curriculum.py:212-215)."""

    learner_id: IDStr
    goal_id: IDStr
    max_steps: int = Field(default=12, ge=1, le=50)
