"""Postgres-backed learner model service."""

from __future__ import annotations

from datetime import date

from schemas.learner_model import (
    AdaptiveLearnerProfile,
    LearnerProfileInput,
    StudentModel,
    classify_mastery,
)

from .settings import LearnerModelSettings
from .stores.repository import LearnerModelRepository


class PostgresLearnerModelService:
    def __init__(self, settings: LearnerModelSettings | None = None) -> None:
        self.settings = settings or LearnerModelSettings()
        self.repo = LearnerModelRepository(self.settings)

    async def get_student_model(self, learner_id: str) -> StudentModel:
        profile = await self.repo.get_profile(learner_id)
        mastery = await self.repo.get_mastery_map(learner_id)
        weak, developing, strong = classify_mastery(mastery)
        last_active = await self.repo.get_last_active(learner_id)
        return StudentModel(
            learner_id=learner_id,
            profile=profile,
            mastery=mastery,
            weak=weak,
            developing=developing,
            strong=strong,
            last_active=last_active,
        )

    async def upsert_mastery(
        self, learner_id: str, concept_id: str, score: float, data_points: int = 1
    ) -> None:
        await self.repo.upsert_mastery(learner_id, concept_id, score, data_points)

    async def get_prerequisites(self, concept_id: str) -> list[str]:
        try:
            from graphrag_service.api import get_graphrag_service

            nodes = await get_graphrag_service().prereqs(concept_id)
            return [node.id for node in nodes]
        except Exception:
            return []

    async def snapshot_week(self, learner_id: str, week_start: date) -> None:
        await self.repo.snapshot_week(learner_id, week_start)

    async def create_profile(self, learner_id: str, profile: LearnerProfileInput) -> AdaptiveLearnerProfile:
        return await self.repo.create_profile(learner_id, profile)

    async def get_profile(self, learner_id: str) -> AdaptiveLearnerProfile | None:
        return await self.repo.get_profile(learner_id)
