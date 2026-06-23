"""In-memory MemoryService fake for API integration tests."""

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

from schemas.errors import NotFoundError
from memory_service.settings import MemorySettings


class FakeMemoryService:
    def __init__(self) -> None:
        self.settings = MemorySettings()
        self._rows: dict[str, MemoryRecord] = {}

    async def write(self, input: MemoryWriteInput, *, agent_id: str) -> MemoryRecord:
        _ = agent_id
        record = MemoryRecord(
            id=str(uuid4()),
            learner_id=input.learner_id,
            type=input.type,
            content=input.content,
            summary=input.summary,
            tags=input.tags,
            provenance=input.provenance,
        )
        self._rows[record.id] = record
        return record

    async def search(self, input: MemorySearchInput) -> list[MemorySearchResult]:
        hits = [
            MemorySearchResult(record=r, score=0.9)
            for r in self._rows.values()
            if r.learner_id == input.learner_id and input.query.lower() in r.content.lower()
        ]
        return hits[: input.k]

    async def get(self, memory_id: str, *, learner_id: str, agent_id: str) -> MemoryRecord | None:
        _ = agent_id
        record = self._rows.get(memory_id)
        if record and record.learner_id == learner_id:
            return record
        return None

    async def update(
        self,
        memory_id: str,
        patch: MemoryUpdateInput,
        *,
        learner_id: str,
        agent_id: str,
    ) -> MemoryRecord:
        _ = agent_id
        record = self._rows.get(memory_id)
        if record is None or record.learner_id != learner_id:
            raise NotFoundError(f"memory not found: {memory_id}")
        data = record.model_dump()
        if patch.content is not None:
            data["content"] = patch.content
        if patch.summary is not None:
            data["summary"] = patch.summary
        if patch.tags is not None:
            data["tags"] = patch.tags
        data["updated_at"] = datetime.now(timezone.utc)
        updated = MemoryRecord.model_validate(data)
        self._rows[memory_id] = updated
        return updated

    async def delete(self, memory_id: str, *, learner_id: str, agent_id: str, hard: bool = False) -> None:
        _ = (agent_id, hard)
        record = self._rows.get(memory_id)
        if record and record.learner_id == learner_id:
            del self._rows[memory_id]

    async def timeline(self, *, learner_id: str, since: str | None = None, until: str | None = None, k: int = 100) -> list[MemoryRecord]:
        _ = (since, until)
        rows = [r for r in self._rows.values() if r.learner_id == learner_id]
        return rows[:k]

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
        _ = learner_id
        return 0

    async def decay_sweep(self, *, learner_id: str | None = None) -> int:
        _ = learner_id
        return 0
