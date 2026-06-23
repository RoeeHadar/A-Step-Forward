"""Thin progress facade until ProgressService lands."""

from __future__ import annotations

from typing import Protocol

from schemas.progress import (
    KnowledgeGaps,
    ProgressSummary,
    StreakInfo,
    UpdateMasteryInput,
    UpdateMasteryResult,
)


class ProgressFacade(Protocol):
    async def snapshot(self, learner_id: str) -> ProgressSummary: ...
    async def gaps(self, learner_id: str) -> KnowledgeGaps: ...
    async def streak(self, learner_id: str) -> StreakInfo: ...
    async def update_mastery(self, inp: UpdateMasteryInput) -> UpdateMasteryResult: ...


class StubProgressFacade:
    """Phase-1 stub — empty snapshots until real progress tracking is online."""

    async def snapshot(self, learner_id: str) -> ProgressSummary:
        return ProgressSummary(learner_id=learner_id, mastery=[])

    async def gaps(self, learner_id: str) -> KnowledgeGaps:
        return KnowledgeGaps(learner_id=learner_id, gaps=[])

    async def streak(self, learner_id: str) -> StreakInfo:
        return StreakInfo(learner_id=learner_id, streak_days=0, next_review_at=None)

    async def update_mastery(self, inp: UpdateMasteryInput) -> UpdateMasteryResult:
        return UpdateMasteryResult(updated=True, entry=None)


def get_progress_facade() -> ProgressFacade:
    return StubProgressFacade()
