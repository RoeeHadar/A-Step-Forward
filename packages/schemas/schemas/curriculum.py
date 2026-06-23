"""Curriculum content schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from ._compat import StrEnum
from .common import IDStr


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


class CourseSummary(BaseModel):
    """Lightweight row for course listings."""

    id: IDStr
    title: str
    level: Level
    summary: str
    unit_count: int = Field(ge=0)
    lesson_count: int = Field(ge=0)


class LessonMatch(BaseModel):
    """Lesson hit from concept search."""

    lesson: Lesson
    course_id: IDStr
    unit_id: IDStr
    matched_concepts: list[IDStr] = Field(default_factory=list)


class PathStep(BaseModel):
    lesson_id: IDStr
    title: str
    est_minutes: int
    reason: str


class LearningPathSuggestion(BaseModel):
    learner_id: IDStr
    goal_id: IDStr
    steps: list[PathStep] = Field(default_factory=list)


