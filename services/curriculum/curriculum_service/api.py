"""Curriculum service contract."""

from __future__ import annotations

from typing import Protocol

from schemas.curriculum import (
    Course,
    CourseSummary,
    LearningPathSuggestion,
    Lesson,
    LessonMatch,
    Level,
)
from schemas.curriculum_seed import SeedBundle


class CurriculumService(Protocol):
    async def upsert_seed(self, bundle: SeedBundle) -> Course: ...

    async def list_courses(self, *, level: Level | None = None, limit: int = 50) -> list[CourseSummary]: ...

    async def get_course(self, course_id: str) -> Course | None: ...

    async def get_lesson(self, lesson_id: str) -> Lesson | None: ...

    async def find_for_concept(self, concept_id: str, *, limit: int = 20) -> list[LessonMatch]: ...

    async def suggest_path(
        self, *, learner_id: str, goal_id: str, max_steps: int = 12
    ) -> LearningPathSuggestion: ...


_service: CurriculumService | None = None


def get_curriculum_service() -> CurriculumService:
    global _service
    if _service is None:
        from .default_service import DefaultCurriculumService

        _service = DefaultCurriculumService()
    return _service
