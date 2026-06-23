"""Curriculum service — Postgres-backed lesson and course retrieval."""

from __future__ import annotations

from schemas.curriculum import Course, Lesson
from schemas.errors import NotFoundError

from curriculum_service.api import get_curriculum_service as get_service


class CurriculumService:
    async def list_courses(self):
        return await get_service().list_courses()

    async def get_course(self, course_id: str) -> Course:
        course = await get_service().get_course(course_id)
        if course is None:
            raise NotFoundError(f"course not found: {course_id}")
        return course

    async def get_lesson(self, lesson_id: str) -> Lesson:
        lesson = await get_service().get_lesson(lesson_id)
        if lesson is None:
            raise NotFoundError(f"lesson not found: {lesson_id}")
        return lesson


_curriculum_service: CurriculumService | None = None


def get_curriculum_service() -> CurriculumService:
    global _curriculum_service
    if _curriculum_service is None:
        _curriculum_service = CurriculumService()
    return _curriculum_service
