"""Learner profile service."""

from __future__ import annotations

from schemas.learners import LearnerProfile, LearnerRole

from ..core.auth import AuthCtx


class LearnerService:
    """Phase-1 in-memory learner profiles keyed by learner_id."""

    def __init__(self) -> None:
        self._profiles: dict[str, LearnerProfile] = {}

    async def get_or_create(self, ctx: AuthCtx) -> LearnerProfile:
        if ctx.learner_id in self._profiles:
            profile = self._profiles[ctx.learner_id]
            profile.child_mode = ctx.child_mode or profile.child_mode
            if ctx.age is not None:
                profile.age = ctx.age
            return profile
        try:
            role = LearnerRole(ctx.role)
        except ValueError:
            role = LearnerRole.LEARNER
        profile = LearnerProfile(
            id=ctx.learner_id,
            clerk_user_id=ctx.clerk_user_id,
            display_name=f"Learner {ctx.learner_id[:8]}",
            role=role,
            age=ctx.age,
            child_mode=ctx.child_mode,
        )
        self._profiles[ctx.learner_id] = profile
        return profile

    async def set_role(self, learner_id: str, role: LearnerRole) -> LearnerProfile:
        """Server-side role assignment (admin tooling / Clerk webhooks)."""
        profile = self._profiles.get(learner_id)
        if profile is None:
            profile = LearnerProfile(id=learner_id, display_name=f"Learner {learner_id[:8]}", role=role)
            self._profiles[learner_id] = profile
        else:
            profile = profile.model_copy(update={"role": role})
            self._profiles[learner_id] = profile
        return profile


_learner_service: LearnerService | None = None


def get_learner_service() -> LearnerService:
    global _learner_service
    if _learner_service is None:
        _learner_service = LearnerService()
    return _learner_service
