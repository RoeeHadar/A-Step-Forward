"""Default curriculum service implementation."""

from __future__ import annotations

from schemas.curriculum import (
    Course,
    CourseSummary,
    LearningPathSuggestion,
    Lesson,
    LessonMatch,
    Level,
    PathStep,
)
from schemas.curriculum_seed import SeedBundle
from schemas.errors import NotFoundError

from .settings import CurriculumSettings
from .stores.repository import CurriculumRepository


class DefaultCurriculumService:
    def __init__(self, settings: CurriculumSettings | None = None) -> None:
        self.settings = settings or CurriculumSettings()
        self.repo = CurriculumRepository(self.settings)

    async def upsert_seed(self, bundle: SeedBundle) -> Course:
        return await self.repo.upsert_seed(bundle)

    async def list_courses(self, *, level: Level | None = None, limit: int = 50) -> list[CourseSummary]:
        return await self.repo.list_courses(level=level, limit=limit)

    async def get_course(self, course_id: str) -> Course | None:
        return await self.repo.get_course(course_id)

    async def get_lesson(self, lesson_id: str) -> Lesson | None:
        return await self.repo.get_lesson(lesson_id)

    async def find_for_concept(self, concept_id: str, *, limit: int = 20) -> list[LessonMatch]:
        return await self.repo.find_for_concept(concept_id, limit=limit)

    async def suggest_path(
        self, *, learner_id: str, goal_id: str, max_steps: int = 12
    ) -> LearningPathSuggestion:
        matches = await self.repo.find_for_concept(goal_id, limit=max_steps)
        if not matches:
            raise NotFoundError(f"no lessons found for concept: {goal_id}")

        steps = [
            PathStep(
                lesson_id=match.lesson.id,
                title=match.lesson.title,
                est_minutes=match.lesson.est_minutes,
                reason=f"covers concept {goal_id}",
            )
            for match in matches[:max_steps]
        ]
        return LearningPathSuggestion(learner_id=learner_id, goal_id=goal_id, steps=steps)
