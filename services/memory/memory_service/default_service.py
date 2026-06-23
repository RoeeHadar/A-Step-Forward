"""Reference implementation of MemoryService."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from schemas.memory import (
    MemoryHealthReport,
    MemoryRecord,
    MemorySearchInput,
    MemorySearchResult,
    MemoryUpdateInput,
    MemoryWriteInput,
)

from .hygiene.audit import audit_event
from .hygiene.compaction import compact_context  # noqa: F401  (re-exported helper)
from .hygiene.conflict_resolution import resolve_conflicts
from .hygiene.consolidation import consolidate_learner
from .hygiene.decay import reinforce, strength_now
from .hygiene.importance import decay_tau_for_importance, score_importance
from .hygiene.pii import redact
from .hygiene.selective_forgetting import run_forgetting_sweep
from .retrieval.hybrid import hybrid_search
from .retrieval.policy import filter_by_policy
from .settings import MemorySettings
from .stores.repository import MemoryRepository


class DefaultMemoryService:
    """Composes stores + hygiene + retrieval."""

    def __init__(self, settings: MemorySettings | None = None) -> None:
        self.settings = settings or MemorySettings()
        self.repo = MemoryRepository(self.settings)

    async def write(self, input: MemoryWriteInput, *, agent_id: str, child_mode: bool = False) -> MemoryRecord:
        from .hygiene.child_mode import assert_affective_allowed

        assert_affective_allowed(input.type, child_mode=child_mode)
        cleaned = await redact(input.content, settings=self.settings)
        importance = await score_importance(cleaned, hint=input.importance_hint, settings=self.settings)
        decay_tau = decay_tau_for_importance(importance, base_tau=self.settings.decay_tau_days)

        record = MemoryRecord(
            id=str(uuid4()),
            learner_id=input.learner_id,
            type=input.type,
            content=cleaned,
            summary=input.summary,
            tags=input.tags,
            valence=input.valence or 0.0,
            salience=importance,
            confidence=importance,
            decay_tau_days=decay_tau,
            provenance=input.provenance,
            expires_at=input.expires_at,
        )

        await resolve_conflicts(self.repo, record, settings=self.settings)
        saved = await self.repo.upsert(record)
        await audit_event("memory.write", agent_id=agent_id, learner_id=input.learner_id, memory_id=saved.id)
        return saved

    async def search(self, input: MemorySearchInput) -> list[MemorySearchResult]:
        candidates = await hybrid_search(self.repo, input)
        allowed = filter_by_policy(candidates, agent_id=input.agent_id)
        for result in allowed:
            reinforced = await self.repo.reinforce(result.record.id, learner_id=input.learner_id)
            if reinforced is not None:
                result.record = reinforced
        await audit_event(
            "memory.search",
            agent_id=input.agent_id,
            learner_id=input.learner_id,
            count=len(allowed),
        )
        return allowed

    async def get(self, memory_id: str, *, learner_id: str, agent_id: str) -> MemoryRecord | None:
        record = await self.repo.get(memory_id, learner_id=learner_id)
        if record:
            reinforced = await self.repo.reinforce(memory_id, learner_id=learner_id)
            if reinforced is not None:
                record = reinforced
            await audit_event("memory.get", agent_id=agent_id, learner_id=learner_id, memory_id=memory_id)
        return record

    async def update(
        self,
        memory_id: str,
        patch: MemoryUpdateInput,
        *,
        learner_id: str,
        agent_id: str,
    ) -> MemoryRecord:
        if patch.content is not None:
            patch = patch.model_copy(update={"content": await redact(patch.content, settings=self.settings)})
        record = await self.repo.patch(memory_id, learner_id=learner_id, patch=patch)
        await audit_event(
            "memory.update", agent_id=agent_id, learner_id=learner_id, memory_id=memory_id, reason=patch.reason
        )
        return record

    async def delete(self, memory_id: str, *, learner_id: str, agent_id: str, hard: bool = False) -> None:
        await self.repo.delete(memory_id, learner_id=learner_id, hard=hard)
        await audit_event("memory.delete", agent_id=agent_id, learner_id=learner_id, memory_id=memory_id, hard=hard)

    async def timeline(
        self,
        *,
        learner_id: str,
        since: str | None = None,
        until: str | None = None,
        k: int = 100,
    ) -> list[MemoryRecord]:
        return await self.repo.timeline(learner_id=learner_id, since=since, until=until, k=k)

    async def dream_now(self, *, learner_id: str) -> MemoryHealthReport:
        now = datetime.now(timezone.utc)
        return MemoryHealthReport(
            learner_id=learner_id,
            window_start=now,
            window_end=now,
            items_reviewed=0,
            items_promoted=0,
            items_archived=0,
            items_merged=0,
            conflicts_resolved=0,
            conflicts_pending=0,
        )

    async def consolidate(self, *, learner_id: str) -> int:
        return await consolidate_learner(
            self.repo,
            learner_id=learner_id,
            cosine=self.settings.consolidation_dup_cosine,
        )

    async def decay_sweep(self, *, learner_id: str | None = None) -> int:
        _ = strength_now, reinforce
        return await run_forgetting_sweep(
            self.repo,
            learner_id=learner_id,
            threshold=self.settings.archive_threshold,
        )
