from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from ._dynamic import FlexibleModel, flexible_model
from .common import IDStr

# AS-111: curriculum content enums and models restored from 3b7d2774 curriculum.py:11-176
# (01c27b73 had replaced them with stubs: Course/Lesson/Objective with id/title only, a
# different Modality). Unchanged from the ref except StrEnum now comes from enum
# (the ref's ._compat shim no longer exists). None of them is in AS90_DECLARED.


class Level(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Modality(StrEnum):
    READING = "reading"
    INTERACTIVE = "interactive"
    VIDEO = "video"
    PROJECT = "project"
    DISCUSSION = "discussion"


class BloomsLevel(StrEnum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class QuestionType(StrEnum):
    MCQ = "mcq"
    SHORT = "short"
    ESSAY = "essay"
    CODE = "code"


class AssessmentType(StrEnum):
    QUIZ = "quiz"
    EXERCISE = "exercise"
    PROJECT = "project"


class ResourceKind(StrEnum):
    ARTICLE = "article"
    VIDEO = "video"
    BOOK = "book"
    INTERACTIVE = "interactive"


class Concept(BaseModel):
    """First-class KG node referenced by objectives and lessons."""

    id: IDStr
    name: str = Field(min_length=1, max_length=128)
    summary: str | None = None
    prerequisites: list[IDStr] = Field(default_factory=list)


class Resource(BaseModel):
    id: IDStr
    kind: ResourceKind
    uri: str
    title: str
    summary: str
    license: str
    minutes: int | None = None


class Question(BaseModel):
    id: IDStr
    stem: str
    type: QuestionType
    choices: list[str] | None = None
    answer: str | None = None
    rubric: str | None = None
    concepts: list[IDStr] = Field(default_factory=list)

    @model_validator(mode="after")
    def _mcq_requires_choices(self) -> Question:
        if self.type == QuestionType.MCQ and not self.choices:
            msg = "MCQ questions require at least one choice"
            raise ValueError(msg)
        return self


class Assessment(BaseModel):
    id: IDStr
    type: AssessmentType
    title: str
    questions: list[Question] = Field(default_factory=list)
    rubric: str
    concepts: list[IDStr] = Field(default_factory=list)


class Objective(BaseModel):
    id: IDStr
    statement: str
    blooms_level: BloomsLevel
    concepts: list[IDStr] = Field(default_factory=list)

    @field_validator("concepts")
    @classmethod
    def _objectives_reference_concepts(cls, concepts: list[IDStr]) -> list[IDStr]:
        if not concepts:
            msg = "objectives must reference at least one concept"
            raise ValueError(msg)
        return concepts


class Lesson(BaseModel):
    id: IDStr
    title: str
    body_md: str
    modality: Modality
    objectives: list[Objective] = Field(default_factory=list)
    concepts: list[IDStr] = Field(default_factory=list)
    resources: list[IDStr] = Field(default_factory=list)
    est_minutes: int = Field(default=15, ge=5, le=180)

    @model_validator(mode="after")
    def _lesson_has_objectives(self) -> Lesson:
        if len(self.objectives) < 2:
            msg = "lessons require at least two objectives"
            raise ValueError(msg)
        return self


class Unit(BaseModel):
    id: IDStr
    title: str
    summary: str
    objectives: list[Objective] = Field(default_factory=list)
    lessons: list[Lesson] = Field(default_factory=list)
    assessments: list[Assessment] = Field(default_factory=list)


class Course(BaseModel):
    id: IDStr
    title: str
    level: Level
    summary: str
    prerequisites: list[IDStr] = Field(default_factory=list)
    units: list[Unit] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)

    @model_validator(mode="after")
    def _course_has_units(self) -> Course:
        if not self.units:
            msg = "courses require at least one unit"
            raise ValueError(msg)
        return self


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


# AS-111: the AS-119 name for the ref Level enum; Level itself is restored above.
CurriculumLevel = Level


class CurriculumListCoursesBody(__getattr__("CurriculumListCoursesInput")):
    """curriculum.list_courses MCP input (3b7d2774 curriculum.py:194-196). level is the
    ref Level enum again, so the repository's level.value filter works as on the ref."""

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
