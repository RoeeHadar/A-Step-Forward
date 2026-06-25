"""Public API for the learner model service."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from schemas.learner_model import AdaptiveLearnerProfile, LearnerProfileInput, StudentModel

from .settings import LearnerModelSettings


class LearnerModelService(Protocol):
    settings: LearnerModelSettings

    async def get_student_model(self, learner_id: str) -> StudentModel: ...
    async def upsert_mastery(
        self, learner_id: str, concept_id: str, score: float, data_points: int = 1
    ) -> None: ...
    async def get_prerequisites(self, concept_id: str) -> list[str]: ...
    async def snapshot_week(self, learner_id: str, week_start: date) -> None: ...
    async def create_profile(self, learner_id: str, profile: LearnerProfileInput) -> AdaptiveLearnerProfile: ...
    async def get_profile(self, learner_id: str) -> AdaptiveLearnerProfile | None: ...


_service: LearnerModelService | None = None


def get_learner_model_service() -> LearnerModelService:
    global _service
    if _service is None:
        from .postgres_service import PostgresLearnerModelService

        _service = PostgresLearnerModelService()
    return _service
