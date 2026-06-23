"""Curriculum repository — Postgres upserts and lookups."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from schemas.curriculum import (
    Concept,
    Course,
    CourseSummary,
    Lesson,
    LessonMatch,
    Level,
)
from schemas.curriculum_seed import SeedBundle

from ..settings import CurriculumSettings
from .database import session_scope
from .models import CurriculumConcept, CurriculumCourse, CurriculumLessonIndex


class CurriculumRepository:
    def __init__(
        self,
        settings: CurriculumSettings,
        *,
        session: AsyncSession | None = None,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.settings = settings
        self._external_session = session
        from .database import get_session_factory

        self._session_factory = session_factory or get_session_factory(settings)

    async def upsert_seed(self, bundle: SeedBundle) -> Course:
        if self._external_session is not None:
            return await self._upsert_seed(self._external_session, bundle)
        async with session_scope(self.settings) as session:
            return await self._upsert_seed(session, bundle)

    async def _upsert_seed(self, session: AsyncSession, bundle: SeedBundle) -> Course:
        course = bundle.course
        await session.execute(delete(CurriculumLessonIndex).where(CurriculumLessonIndex.course_id == course.id))
        await session.execute(delete(CurriculumConcept).where(CurriculumConcept.course_id == course.id))

        course_stmt = insert(CurriculumCourse).values(
            id=course.id,
            title=course.title,
            level=course.level.value,
            summary=course.summary,
            prerequisites=course.prerequisites,
            payload=course.model_dump(mode="json"),
            published=True,
        )
        course_stmt = course_stmt.on_conflict_do_update(
            index_elements=[CurriculumCourse.id],
            set_={
                "title": course.title,
                "level": course.level.value,
                "summary": course.summary,
                "prerequisites": course.prerequisites,
                "payload": course.model_dump(mode="json"),
                "published": True,
            },
        )
        await session.execute(course_stmt)

        for concept in bundle.concepts:
            await session.execute(
                insert(CurriculumConcept)
                .values(
                    id=concept.id,
                    course_id=course.id,
                    name=concept.name,
                    summary=concept.summary,
                    prerequisites=concept.prerequisites,
                    payload=concept.model_dump(mode="json"),
                )
                .on_conflict_do_update(
                    index_elements=[CurriculumConcept.id],
                    set_={
                        "course_id": course.id,
                        "name": concept.name,
                        "summary": concept.summary,
                        "prerequisites": concept.prerequisites,
                        "payload": concept.model_dump(mode="json"),
                    },
                )
            )

        sort_order = 0
        for unit in course.units:
            for lesson in unit.lessons:
                concepts = sorted(set(lesson.concepts) | _objective_concepts(lesson))
                await session.execute(
                    insert(CurriculumLessonIndex)
                    .values(
                        id=lesson.id,
                        course_id=course.id,
                        unit_id=unit.id,
                        title=lesson.title,
                        concepts=concepts,
                        est_minutes=lesson.est_minutes,
                        sort_order=sort_order,
                        payload=lesson.model_dump(mode="json"),
                    )
                    .on_conflict_do_update(
                        index_elements=[CurriculumLessonIndex.id],
                        set_={
                            "course_id": course.id,
                            "unit_id": unit.id,
                            "title": lesson.title,
                            "concepts": concepts,
                            "est_minutes": lesson.est_minutes,
                            "sort_order": sort_order,
                            "payload": lesson.model_dump(mode="json"),
                        },
                    )
                )
                sort_order += 1

        await session.commit()
        return course

    async def list_courses(self, *, level: Level | None = None, limit: int = 50) -> list[CourseSummary]:
        async with session_scope(self.settings) as session:
            stmt = select(CurriculumCourse).where(CurriculumCourse.published.is_(True))
            if level is not None:
                stmt = stmt.where(CurriculumCourse.level == level.value)
            stmt = stmt.limit(limit)
            rows = (await session.scalars(stmt)).all()
            summaries: list[CourseSummary] = []
            for row in rows:
                course = Course.model_validate(row.payload)
                lesson_count = sum(len(unit.lessons) for unit in course.units)
                summaries.append(
                    CourseSummary(
                        id=course.id,
                        title=course.title,
                        level=course.level,
                        summary=course.summary,
                        unit_count=len(course.units),
                        lesson_count=lesson_count,
                    )
                )
            return summaries

    async def get_course(self, course_id: str) -> Course | None:
        async with session_scope(self.settings) as session:
            row = await session.get(CurriculumCourse, course_id)
            if row is None or not row.published:
                return None
            return Course.model_validate(row.payload)

    async def get_lesson(self, lesson_id: str) -> Lesson | None:
        async with session_scope(self.settings) as session:
            row = await session.get(CurriculumLessonIndex, lesson_id)
            if row is None:
                return None
            return Lesson.model_validate(row.payload)

    async def find_for_concept(self, concept_id: str, *, limit: int = 20) -> list[LessonMatch]:
        async with session_scope(self.settings) as session:
            stmt = (
                select(CurriculumLessonIndex)
                .where(CurriculumLessonIndex.concepts.contains([concept_id]))
                .order_by(CurriculumLessonIndex.sort_order)
                .limit(limit)
            )
            rows = (await session.scalars(stmt)).all()
            return [
                LessonMatch(
                    lesson=Lesson.model_validate(row.payload),
                    course_id=row.course_id,
                    unit_id=row.unit_id,
                    matched_concepts=[concept_id],
                )
                for row in rows
            ]

    async def list_concepts(self, course_id: str) -> list[Concept]:
        async with session_scope(self.settings) as session:
            stmt = select(CurriculumConcept).where(CurriculumConcept.course_id == course_id)
            rows = (await session.scalars(stmt)).all()
            return [Concept.model_validate(row.payload) for row in rows]


def _objective_concepts(lesson: Lesson) -> set[str]:
    concepts: set[str] = set()
    for objective in lesson.objectives:
        concepts.update(objective.concepts)
    return concepts
