"""Learning plan persistence and content lookups."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from schemas.learning_path import BagrutRef, ContentSectionRef, LearningPlan, PlanConcept, PlanWeek
from schemas.errors import NotFoundError

from ..settings import LearningPathSettings
from .database import session_scope
from .models import LearningPlanRow, PlanWeekRow


def _concept_name(concept_id: str) -> str:
    return concept_id.replace("_", " ").replace("-", " ").strip().title()


class LearningPathRepository:
    def __init__(
        self,
        settings: LearningPathSettings,
        *,
        session: AsyncSession | None = None,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.settings = settings
        self._external_session = session
        from .database import get_session_factory

        self._session_factory = session_factory or get_session_factory(settings)

    async def find_sections(self, subject: str, limit: int = 5) -> list[ContentSectionRef]:
        if self._external_session is not None:
            return await self._find_sections(self._external_session, subject, limit)
        async with session_scope(self.settings) as session:
            return await self._find_sections(session, subject, limit)

    async def _find_sections(
        self, session: AsyncSession, subject: str, limit: int
    ) -> list[ContentSectionRef]:
        result = await session.execute(
            text(
                """
                SELECT id::text, title, chunk_index, page_start
                FROM content_sections
                WHERE subject = :subject
                ORDER BY chunk_index
                LIMIT :limit
                """
            ),
            {"subject": subject, "limit": limit},
        )
        return [
            ContentSectionRef(
                id=row["id"],
                title=row["title"],
                chunk_index=row.get("chunk_index"),
                page_start=row.get("page_start"),
            )
            for row in result.mappings().all()
        ]

    async def find_bagrut(self, subject: str, limit: int = 3) -> list[BagrutRef]:
        if self._external_session is not None:
            return await self._find_bagrut(self._external_session, subject, limit)
        async with session_scope(self.settings) as session:
            return await self._find_bagrut(session, subject, limit)

    async def _find_bagrut(self, session: AsyncSession, subject: str, limit: int) -> list[BagrutRef]:
        result = await session.execute(
            text(
                """
                SELECT display_name, file_url, year, exam_type
                FROM bagrut_exams
                WHERE subject = :subject
                ORDER BY year DESC NULLS LAST, display_name
                LIMIT :limit
                """
            ),
            {"subject": subject, "limit": limit},
        )
        return [
            BagrutRef(
                display_name=row["display_name"],
                file_url=row["file_url"],
                year=row.get("year"),
                exam_type=row.get("exam_type"),
            )
            for row in result.mappings().all()
        ]

    async def replace_plan(
        self,
        learner_id: str,
        goal: str,
        week_groups: list[list[PlanConcept]],
        *,
        start_date: date | None = None,
    ) -> LearningPlan:
        if self._external_session is not None:
            return await self._replace_plan(
                self._external_session, learner_id, goal, week_groups, start_date=start_date
            )
        async with session_scope(self.settings) as session:
            plan = await self._replace_plan(session, learner_id, goal, week_groups, start_date=start_date)
            await session.commit()
            return plan

    async def _replace_plan(
        self,
        session: AsyncSession,
        learner_id: str,
        goal: str,
        week_groups: list[list[PlanConcept]],
        *,
        start_date: date | None = None,
    ) -> LearningPlan:
        existing = await session.execute(
            select(LearningPlanRow).where(LearningPlanRow.learner_id == learner_id)
        )
        old = existing.scalar_one_or_none()
        if old is not None:
            await session.execute(delete(PlanWeekRow).where(PlanWeekRow.plan_id == old.id))
            await session.delete(old)
            await session.flush()

        plan_start = start_date or date.today()
        plan_row = LearningPlanRow(
            learner_id=learner_id,
            goal=goal,
            start_date=plan_start,
            end_date=plan_start + timedelta(days=7 * len(week_groups)),
            status="active",
        )
        session.add(plan_row)
        await session.flush()

        weeks: list[PlanWeek] = []
        for week_number, concepts in enumerate(week_groups, start=1):
            concept_ids = [c.concept_id for c in concepts]
            content_ids = [s.id for c in concepts for s in c.suggested_sections]
            status = "active" if week_number == 1 else "upcoming"
            quiz_due = datetime.combine(
                plan_start + timedelta(days=7 * week_number),
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
            week_row = PlanWeekRow(
                plan_id=plan_row.id,
                week_number=week_number,
                concepts=concept_ids,
                content_ids=[UUID(cid) for cid in content_ids] if content_ids else None,
                quiz_due_at=quiz_due,
                status=status,
            )
            session.add(week_row)
            await session.flush()
            weeks.append(
                PlanWeek(
                    id=str(week_row.id),
                    plan_id=str(plan_row.id),
                    week_number=week_number,
                    concepts=concepts,
                    content_ids=content_ids or None,
                    quiz_due_at=quiz_due,
                    status=status,
                )
            )

        return LearningPlan(
            id=str(plan_row.id),
            learner_id=learner_id,
            goal=goal,
            start_date=plan_start,
            end_date=plan_row.end_date,
            status=plan_row.status,
            weeks=weeks,
        )

    async def get_current_plan(self, learner_id: str) -> LearningPlan | None:
        if self._external_session is not None:
            return await self._get_current_plan(self._external_session, learner_id)
        async with session_scope(self.settings) as session:
            return await self._get_current_plan(session, learner_id)

    async def _get_current_plan(self, session: AsyncSession, learner_id: str) -> LearningPlan | None:
        result = await session.execute(
            select(LearningPlanRow).where(
                LearningPlanRow.learner_id == learner_id,
                LearningPlanRow.status == "active",
            )
        )
        plan_row = result.scalar_one_or_none()
        if plan_row is None:
            return None
        return await self._plan_from_row(session, plan_row)

    async def get_week(self, plan_id: str, week_number: int, learner_id: str) -> PlanWeek:
        if self._external_session is not None:
            return await self._get_week(self._external_session, plan_id, week_number, learner_id)
        async with session_scope(self.settings) as session:
            return await self._get_week(session, plan_id, week_number, learner_id)

    async def _get_week(
        self, session: AsyncSession, plan_id: str, week_number: int, learner_id: str
    ) -> PlanWeek:
        try:
            plan_uuid = UUID(plan_id)
        except ValueError as exc:
            raise NotFoundError("Learning plan not found") from exc

        plan_result = await session.execute(
            select(LearningPlanRow).where(
                LearningPlanRow.id == plan_uuid,
                LearningPlanRow.learner_id == learner_id,
            )
        )
        plan_row = plan_result.scalar_one_or_none()
        if plan_row is None:
            raise NotFoundError("Learning plan not found")

        week_result = await session.execute(
            select(PlanWeekRow).where(
                PlanWeekRow.plan_id == plan_row.id,
                PlanWeekRow.week_number == week_number,
            )
        )
        week_row = week_result.scalar_one_or_none()
        if week_row is None:
            raise NotFoundError("Plan week not found")

        concepts = await self._hydrate_concepts(session, week_row.concepts, learner_id)
        return PlanWeek(
            id=str(week_row.id),
            plan_id=str(week_row.plan_id),
            week_number=week_row.week_number,
            concepts=concepts,
            content_ids=[str(cid) for cid in (week_row.content_ids or [])],
            quiz_due_at=week_row.quiz_due_at,
            status=week_row.status,
        )

    async def _plan_from_row(self, session: AsyncSession, plan_row: LearningPlanRow) -> LearningPlan:
        weeks_result = await session.execute(
            select(PlanWeekRow)
            .where(PlanWeekRow.plan_id == plan_row.id)
            .order_by(PlanWeekRow.week_number)
        )
        week_rows = weeks_result.scalars().all()
        weeks: list[PlanWeek] = []
        for week_row in week_rows:
            concepts = await self._hydrate_concepts(session, week_row.concepts, plan_row.learner_id)
            weeks.append(
                PlanWeek(
                    id=str(week_row.id),
                    plan_id=str(week_row.plan_id),
                    week_number=week_row.week_number,
                    concepts=concepts,
                    content_ids=[str(cid) for cid in (week_row.content_ids or [])],
                    quiz_due_at=week_row.quiz_due_at,
                    status=week_row.status,
                )
            )
        return LearningPlan(
            id=str(plan_row.id),
            learner_id=plan_row.learner_id,
            goal=plan_row.goal,
            start_date=plan_row.start_date,
            end_date=plan_row.end_date,
            status=plan_row.status,
            weeks=weeks,
        )

    async def _hydrate_concepts(
        self, session: AsyncSession, concept_ids: list[str], learner_id: str
    ) -> list[PlanConcept]:
        mastery_result = await session.execute(
            text(
                """
                SELECT concept_id, score::float AS score
                FROM concept_mastery
                WHERE learner_id = :learner_id AND concept_id = ANY(:ids)
                """
            ),
            {"learner_id": learner_id, "ids": concept_ids},
        )
        mastery_map = {row["concept_id"]: float(row["score"]) for row in mastery_result.mappings().all()}

        profile_subjects: list[str] = []
        profile_result = await session.execute(
            text("SELECT subjects FROM learner_profiles WHERE learner_id = :learner_id"),
            {"learner_id": learner_id},
        )
        profile_row = profile_result.mappings().first()
        if profile_row and profile_row.get("subjects"):
            profile_subjects = list(profile_row["subjects"])

        concepts: list[PlanConcept] = []
        for concept_id in concept_ids:
            from ..engine import infer_subject

            subject = infer_subject(concept_id, profile_subjects)
            sections = await self._find_sections(session, subject, 5)
            bagrut = await self._find_bagrut(session, subject, 3)
            concepts.append(
                PlanConcept(
                    concept_id=concept_id,
                    name=_concept_name(concept_id),
                    subject=subject,
                    mastery=mastery_map.get(concept_id),
                    suggested_sections=sections,
                    recommended_bagrut=bagrut,
                )
            )
        return concepts
