"""Memory repository — Postgres + pgvector facade over per-type stores."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from schemas.memory import MemoryRecord, MemoryType, MemoryUpdateInput
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..settings import MemorySettings
from .database import get_session_factory, session_scope
from .mappers import table_for_type
from .type_repositories import (
    TypedMemoryRepository,
    all_persisted_types,
    locate_record,
    repo_for_type,
)


class MemoryRepository:
    """Routes memory CRUD to the correct type-specific Postgres table."""

    def __init__(
        self,
        settings: MemorySettings,
        *,
        session: AsyncSession | None = None,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.settings = settings
        self._external_session = session
        self._session_factory = session_factory or get_session_factory(settings)

    def _typed(self, session: AsyncSession, memory_type: MemoryType) -> TypedMemoryRepository:
        return repo_for_type(session, memory_type)

    async def upsert(self, record: MemoryRecord, *, embedding: list[float] | None = None) -> MemoryRecord:
        if record.type == MemoryType.WORKING:
            raise ValueError("Working memory is ephemeral and cannot be persisted")
        if self._external_session is not None:
            return await self._typed(self._external_session, record.type).upsert(record, embedding=embedding)
        async with session_scope(self.settings) as session:
            return await self._typed(session, record.type).upsert(record, embedding=embedding)

    async def get(self, memory_id: str, *, learner_id: str) -> MemoryRecord | None:
        if self._external_session is not None:
            located = await locate_record(self._external_session, memory_id)
            if located is None:
                return None
            record, _ = located
            if record.learner_id != learner_id or record.deleted_at is not None:
                return None
            return record
        async with session_scope(self.settings) as session:
            located = await locate_record(session, memory_id)
            if located is None:
                return None
            record, _ = located
            if record.learner_id != learner_id or record.deleted_at is not None:
                return None
            return record

    async def patch(self, memory_id: str, *, learner_id: str, patch: MemoryUpdateInput) -> MemoryRecord:
        if self._external_session is not None:
            located = await locate_record(self._external_session, memory_id)
            if located is None:
                raise KeyError(memory_id)
            _, memory_type = located
            return await self._typed(self._external_session, memory_type).patch(
                memory_id, learner_id=learner_id, patch=patch
            )
        async with session_scope(self.settings) as session:
            located = await locate_record(session, memory_id)
            if located is None:
                raise KeyError(memory_id)
            _, memory_type = located
            return await self._typed(session, memory_type).patch(memory_id, learner_id=learner_id, patch=patch)

    async def delete(self, memory_id: str, *, learner_id: str, hard: bool = False) -> None:
        if self._external_session is not None:
            await self._delete_in_session(self._external_session, memory_id, learner_id=learner_id, hard=hard)
            return
        async with session_scope(self.settings) as session:
            await self._delete_in_session(session, memory_id, learner_id=learner_id, hard=hard)

    async def _delete_in_session(
        self,
        session: AsyncSession,
        memory_id: str,
        *,
        learner_id: str,
        hard: bool,
    ) -> None:
        located = await locate_record(session, memory_id)
        if located is None:
            return
        _, memory_type = located
        repo = self._typed(session, memory_type)
        if hard:
            await repo.hard_delete(memory_id, learner_id=learner_id)
        else:
            await repo.soft_delete(memory_id, learner_id=learner_id)

    async def timeline(
        self,
        *,
        learner_id: str,
        since: str | None = None,
        until: str | None = None,
        k: int = 100,
    ) -> list[MemoryRecord]:
        since_dt = _parse_iso(since)
        until_dt = _parse_iso(until)
        if self._external_session is not None:
            return await self._timeline_in_session(
                self._external_session,
                learner_id=learner_id,
                since=since_dt,
                until=until_dt,
                k=k,
            )
        async with session_scope(self.settings) as session:
            return await self._timeline_in_session(
                session,
                learner_id=learner_id,
                since=since_dt,
                until=until_dt,
                k=k,
            )

    async def _timeline_in_session(
        self,
        session: AsyncSession,
        *,
        learner_id: str,
        since: datetime | None,
        until: datetime | None,
        k: int,
    ) -> list[MemoryRecord]:
        rows: list[MemoryRecord] = []
        for memory_type in all_persisted_types():
            rows.extend(
                await self._typed(session, memory_type).list_for_learner(
                    learner_id=learner_id,
                    since=since,
                    until=until,
                    include_deleted=False,
                    include_archived=True,
                )
            )
        rows.sort(key=lambda r: r.created_at, reverse=True)
        return rows[:k]

    async def iter_for_learner(self, learner_id: str) -> Iterable[MemoryRecord]:
        if self._external_session is not None:
            return await self._collect_for_learner(self._external_session, learner_id)
        async with session_scope(self.settings) as session:
            return await self._collect_for_learner(session, learner_id)

    async def _collect_for_learner(self, session: AsyncSession, learner_id: str) -> list[MemoryRecord]:
        rows: list[MemoryRecord] = []
        for memory_type in all_persisted_types():
            rows.extend(
                await self._typed(session, memory_type).list_for_learner(
                    learner_id=learner_id,
                    include_deleted=False,
                    include_archived=False,
                )
            )
        return rows

    async def archive_below_threshold(self, *, learner_id: str | None, threshold: float) -> int:
        now = datetime.now(timezone.utc)
        if self._external_session is not None:
            return await self._archive_in_session(
                self._external_session,
                learner_id=learner_id,
                threshold=threshold,
                now=now,
            )
        async with session_scope(self.settings) as session:
            return await self._archive_in_session(session, learner_id=learner_id, threshold=threshold, now=now)

    async def _archive_in_session(
        self,
        session: AsyncSession,
        *,
        learner_id: str | None,
        threshold: float,
        now: datetime,
    ) -> int:
        total = 0
        for memory_type in all_persisted_types():
            total += await self._typed(session, memory_type).archive_below_threshold(
                learner_id=learner_id,
                threshold=threshold,
                now=now,
            )
        return total

    async def list_by_types(self, learner_id: str, types: set[MemoryType]) -> list[MemoryRecord]:
        if self._external_session is not None:
            return await self._list_by_types_in_session(self._external_session, learner_id, types)
        async with session_scope(self.settings) as session:
            return await self._list_by_types_in_session(session, learner_id, types)

    async def _list_by_types_in_session(
        self,
        session: AsyncSession,
        learner_id: str,
        types: set[MemoryType],
    ) -> list[MemoryRecord]:
        rows: list[MemoryRecord] = []
        for memory_type in types:
            if memory_type == MemoryType.WORKING:
                continue
            rows.extend(
                await self._typed(session, memory_type).list_active_for_learner(learner_id=learner_id)
            )
        return rows

    async def reinforce(self, memory_id: str, *, learner_id: str, delta: float = 0.05) -> MemoryRecord | None:
        if self._external_session is not None:
            located = await locate_record(self._external_session, memory_id)
            if located is None:
                return None
            _, memory_type = located
            return await self._typed(self._external_session, memory_type).reinforce(
                memory_id, learner_id=learner_id, delta=delta
            )
        async with session_scope(self.settings) as session:
            located = await locate_record(session, memory_id)
            if located is None:
                return None
            _, memory_type = located
            return await self._typed(session, memory_type).reinforce(memory_id, learner_id=learner_id, delta=delta)

    async def set_embedding(self, memory_id: str, memory_type: MemoryType, embedding: list[float]) -> None:
        table = table_for_type(memory_type)
        if self._external_session is not None:
            row = await self._external_session.get(table, memory_id)
            if row is not None:
                row.embedding = embedding
                await self._external_session.flush()
            return
        async with session_scope(self.settings) as session:
            row = await session.get(table, memory_id)
            if row is not None:
                row.embedding = embedding


def _parse_iso(value: str | None) -> datetime | None:
    if value is None:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)
