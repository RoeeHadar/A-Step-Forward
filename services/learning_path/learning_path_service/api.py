"""Learning path service protocol."""

from __future__ import annotations

from typing import Protocol

from schemas.learning_path import LearningPlan, PlanWeek

from .settings import LearningPathSettings


class LearningPathService(Protocol):
    settings: LearningPathSettings

    async def generate_plan(self, learner_id: str) -> LearningPlan: ...
    async def get_current_plan(self, learner_id: str) -> LearningPlan | None: ...
    async def get_week(self, learner_id: str, plan_id: str, week_number: int) -> PlanWeek: ...


_service: LearningPathService | None = None


def get_learning_path_service() -> LearningPathService:
    global _service
    if _service is None:
        from .postgres_service import PostgresLearningPathService

        _service = PostgresLearningPathService()
    return _service
