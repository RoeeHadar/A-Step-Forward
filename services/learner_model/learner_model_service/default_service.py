"""In-memory learner model service for tests."""

from __future__ import annotations

from datetime import date, datetime, timezone

from schemas.learner_model import (
    AdaptiveLearnerProfile,
    LearnerProfileInput,
    StudentModel,
    classify_mastery,
    self_score_to_mastery,
)

from .settings import LearnerModelSettings


class DefaultLearnerModelService:
    def __init__(self, settings: LearnerModelSettings | None = None) -> None:
        self.settings = settings or LearnerModelSettings()
        self._profiles: dict[str, AdaptiveLearnerProfile] = {}
        self._mastery: dict[str, dict[str, float]] = {}
        self._last_active: dict[str, datetime] = {}

    async def get_student_model(self, learner_id: str) -> StudentModel:
        mastery = dict(self._mastery.get(learner_id, {}))
        weak, developing, strong = classify_mastery(mastery)
        return StudentModel(
            learner_id=learner_id,
            profile=self._profiles.get(learner_id),
            mastery=mastery,
            weak=weak,
            developing=developing,
            strong=strong,
            last_active=self._last_active.get(learner_id),
        )

    async def upsert_mastery(
        self, learner_id: str, concept_id: str, score: float, data_points: int = 1
    ) -> None:
        bucket = self._mastery.setdefault(learner_id, {})
        bucket[concept_id] = max(0.0, min(1.0, score))
        self._last_active[learner_id] = datetime.now(timezone.utc)

    async def get_prerequisites(self, concept_id: str) -> list[str]:
        return []

    async def snapshot_week(self, learner_id: str, week_start: date) -> None:
        return None

    async def create_profile(self, learner_id: str, profile: LearnerProfileInput) -> AdaptiveLearnerProfile:
        now = datetime.now(timezone.utc)
        adaptive = AdaptiveLearnerProfile(
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
            created_at=now,
            updated_at=now,
        )
        self._profiles[learner_id] = adaptive
        for concept_id, raw in profile.self_scores.items():
            await self.upsert_mastery(learner_id, concept_id, self_score_to_mastery(raw))
        return adaptive

    async def get_profile(self, learner_id: str) -> AdaptiveLearnerProfile | None:
        return self._profiles.get(learner_id)
