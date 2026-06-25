"""Learner model persistence."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from schemas.learner_model import (
    AdaptiveLearnerProfile,
    LearnerProfileInput,
    classify_mastery,
    self_score_to_mastery,
)

from ..settings import LearnerModelSettings
from .database import session_scope
from .models import ConceptMasteryRow, LearnerProfileRow, MasterySnapshotRow


def _row_to_profile(row: LearnerProfileRow) -> AdaptiveLearnerProfile:
    return AdaptiveLearnerProfile(
        learner_id=row.learner_id,
        goal=row.goal,
        grade_level=row.grade_level,
        points_group=row.points_group,
        subjects=list(row.subjects),
        hours_per_week=float(row.hours_per_week),
        preferred_style=row.preferred_style,
        attention_span=row.attention_span,
        self_scores=row.self_scores,
        background_notes=row.background_notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class LearnerModelRepository:
    def __init__(
        self,
        settings: LearnerModelSettings,
        *,
        session: AsyncSession | None = None,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.settings = settings
        self._external_session = session
        from .database import get_session_factory

        self._session_factory = session_factory or get_session_factory(settings)

    async def get_profile(self, learner_id: str) -> AdaptiveLearnerProfile | None:
        if self._external_session is not None:
            return await self._get_profile(self._external_session, learner_id)
        async with session_scope(self.settings) as session:
            return await self._get_profile(session, learner_id)

    async def _get_profile(self, session: AsyncSession, learner_id: str) -> AdaptiveLearnerProfile | None:
        result = await session.execute(
            select(LearnerProfileRow).where(LearnerProfileRow.learner_id == learner_id)
        )
        row = result.scalar_one_or_none()
        return _row_to_profile(row) if row else None

    async def create_profile(self, learner_id: str, profile: LearnerProfileInput) -> AdaptiveLearnerProfile:
        if self._external_session is not None:
            return await self._create_profile(self._external_session, learner_id, profile)
        async with session_scope(self.settings) as session:
            return await self._create_profile(session, learner_id, profile)

    async def _create_profile(
        self, session: AsyncSession, learner_id: str, profile: LearnerProfileInput
    ) -> AdaptiveLearnerProfile:
        stmt = insert(LearnerProfileRow).values(
            learner_id=learner_id,
            goal=profile.goal,
            grade_level=profile.grade_level,
            points_group=profile.points_group,
            subjects=profile.subjects,
            hours_per_week=profile.hours_per_week,
            preferred_style=profile.preferred_style,
            attention_span=profile.attention_span,
            self_scores=profile.self_scores,
            background_notes=profile.background_notes,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[LearnerProfileRow.learner_id],
            set_={
                "goal": profile.goal,
                "grade_level": profile.grade_level,
                "points_group": profile.points_group,
                "subjects": profile.subjects,
                "hours_per_week": profile.hours_per_week,
                "preferred_style": profile.preferred_style,
                "attention_span": profile.attention_span,
                "self_scores": profile.self_scores,
                "background_notes": profile.background_notes,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        await session.execute(stmt)

        for concept_id, raw_score in profile.self_scores.items():
            await self._upsert_mastery(
                session,
                learner_id,
                concept_id,
                self_score_to_mastery(raw_score),
                data_points=1,
            )

        await session.commit()
        result = await self._get_profile(session, learner_id)
        assert result is not None
        return result

    async def upsert_mastery(
        self, learner_id: str, concept_id: str, score: float, data_points: int = 1
    ) -> None:
        if self._external_session is not None:
            await self._upsert_mastery(
                self._external_session, learner_id, concept_id, score, data_points
            )
            await self._external_session.commit()
            return
        async with session_scope(self.settings) as session:
            await self._upsert_mastery(session, learner_id, concept_id, score, data_points)
            await session.commit()

    async def _upsert_mastery(
        self,
        session: AsyncSession,
        learner_id: str,
        concept_id: str,
        score: float,
        data_points: int,
    ) -> None:
        clamped = max(0.0, min(1.0, score))
        stmt = insert(ConceptMasteryRow).values(
            learner_id=learner_id,
            concept_id=concept_id,
            score=clamped,
            data_points=data_points,
            last_activity=datetime.now(timezone.utc),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[ConceptMasteryRow.learner_id, ConceptMasteryRow.concept_id],
            set_={
                "score": clamped,
                "data_points": ConceptMasteryRow.data_points + data_points,
                "last_activity": datetime.now(timezone.utc),
            },
        )
        await session.execute(stmt)

    async def get_mastery_map(self, learner_id: str) -> dict[str, float]:
        if self._external_session is not None:
            return await self._get_mastery_map(self._external_session, learner_id)
        async with session_scope(self.settings) as session:
            return await self._get_mastery_map(session, learner_id)

    async def _get_mastery_map(self, session: AsyncSession, learner_id: str) -> dict[str, float]:
        result = await session.execute(
            select(ConceptMasteryRow).where(ConceptMasteryRow.learner_id == learner_id)
        )
        rows = result.scalars().all()
        return {row.concept_id: float(row.score) for row in rows}

    async def get_last_active(self, learner_id: str) -> datetime | None:
        if self._external_session is not None:
            return await self._get_last_active(self._external_session, learner_id)
        async with session_scope(self.settings) as session:
            return await self._get_last_active(session, learner_id)

    async def _get_last_active(self, session: AsyncSession, learner_id: str) -> datetime | None:
        result = await session.execute(
            select(ConceptMasteryRow.last_activity)
            .where(ConceptMasteryRow.learner_id == learner_id)
            .order_by(ConceptMasteryRow.last_activity.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def snapshot_week(self, learner_id: str, week_start: date) -> None:
        mastery = await self.get_mastery_map(learner_id)
        weak, developing, strong = classify_mastery(mastery)
        payload = {
            "mastery": mastery,
            "weak": weak,
            "developing": developing,
            "strong": strong,
        }
        if self._external_session is not None:
            await self._snapshot_week(self._external_session, learner_id, week_start, payload)
            await self._external_session.commit()
            return
        async with session_scope(self.settings) as session:
            await self._snapshot_week(session, learner_id, week_start, payload)
            await session.commit()

    async def _snapshot_week(
        self,
        session: AsyncSession,
        learner_id: str,
        week_start: date,
        scores: dict,
    ) -> None:
        stmt = insert(MasterySnapshotRow).values(
            learner_id=learner_id,
            week_start=week_start,
            scores=scores,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[MasterySnapshotRow.learner_id, MasterySnapshotRow.week_start],
            set_={"scores": scores},
        )
        await session.execute(stmt)
