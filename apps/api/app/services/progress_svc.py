"""Progress service — Phase-1 stub aligned with progress MCP shape."""

from __future__ import annotations

from schemas.progress import MasteryEntry, ProgressSummary

from ..core.auth import AuthCtx


class ProgressService:
    async def snapshot(self, ctx: AuthCtx) -> ProgressSummary:
        return ProgressSummary(
            learner_id=ctx.learner_id,
            mastery=[
                MasteryEntry(
                    concept_id="concept-fraction",
                    concept_title="Fractions",
                    score=0.35,
                )
            ],
            streak_days=0,
            next_review_at=None,
        )


_progress_service: ProgressService | None = None


def get_progress_service() -> ProgressService:
    global _progress_service
    if _progress_service is None:
        _progress_service = ProgressService()
    return _progress_service
