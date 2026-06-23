"""Per-type memory repositories backed by Postgres + pgvector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from schemas.memory import MemoryRecord, MemoryType, MemoryUpdateInput
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .mappers import record_to_row, row_to_record, table_for_type, type_for_table
from .models import MEMORY_TABLES, MemoryColumnsMixin


class TypedMemoryRepository:
    """CRUD for a single persisted memory type."""

    def __init__(self, session: AsyncSession, memory_type: MemoryType) -> None:
        self.session = session
        self.memory_type = memory_type
        self.table = table_for_type(memory_type)

    async def upsert(self, record: MemoryRecord, *, embedding: list[float] | None = None) -> MemoryRecord:
        record.updated_at = datetime.now(timezone.utc)
        existing = await self.session.get(self.table, record.id)
        if existing is None:
            row = record_to_row(record, embedding=embedding)
            self.session.add(row)
        else:
            self._apply_record(existing, record, embedding=embedding)
        await self.session.flush()
        refreshed = await self.session.get(self.table, record.id)
        assert refreshed is not None
        return row_to_record(refreshed, self.memory_type)

    async def get(self, memory_id: str, *, learner_id: str) -> MemoryRecord | None:
        row = await self.session.get(self.table, memory_id)
        if row is None or row.learner_id != learner_id or row.deleted_at is not None:
            return None
        return row_to_record(row, self.memory_type)

    async def patch(self, memory_id: str, *, learner_id: str, patch: MemoryUpdateInput) -> MemoryRecord:
        row = await self.session.get(self.table, memory_id)
        if row is None or row.learner_id != learner_id or row.deleted_at is not None:
            raise KeyError(memory_id)
        if patch.content is not None:
            row.content = patch.content
        if patch.summary is not None:
            row.summary = patch.summary
        if patch.tags is not None:
            row.tags = patch.tags
        if patch.salience is not None:
            row.salience = patch.salience
        if patch.confidence is not None:
            row.confidence = patch.confidence
        row.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return row_to_record(row, self.memory_type)

    async def soft_delete(self, memory_id: str, *, learner_id: str) -> None:
        row = await self.session.get(self.table, memory_id)
        if row is None or row.learner_id != learner_id:
            return
        row.deleted_at = datetime.now(timezone.utc)
        row.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def hard_delete(self, memory_id: str, *, learner_id: str) -> None:
        row = await self.session.get(self.table, memory_id)
        if row is None or row.learner_id != learner_id:
            return
        await self.session.delete(row)
        await self.session.flush()

    async def list_for_learner(
        self,
        *,
        learner_id: str,
        since: datetime | None = None,
        until: datetime | None = None,
        include_deleted: bool = False,
        include_archived: bool = True,
        limit: int | None = None,
    ) -> list[MemoryRecord]:
        stmt = select(self.table).where(self.table.learner_id == learner_id)
        if not include_deleted:
            stmt = stmt.where(self.table.deleted_at.is_(None))
        if not include_archived:
            stmt = stmt.where(self.table.archived_at.is_(None))
        if since is not None:
            stmt = stmt.where(self.table.created_at >= since)
        if until is not None:
            stmt = stmt.where(self.table.created_at <= until)
        stmt = stmt.order_by(self.table.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        rows = (await self.session.scalars(stmt)).all()
        return [row_to_record(row, self.memory_type) for row in rows]

    async def archive_below_threshold(self, *, learner_id: str | None, threshold: float, now: datetime) -> int:
        from ..hygiene.decay import strength_now

        stmt = select(self.table).where(
            self.table.deleted_at.is_(None),
            self.table.archived_at.is_(None),
        )
        if learner_id is not None:
            stmt = stmt.where(self.table.learner_id == learner_id)
        rows = (await self.session.scalars(stmt)).all()
        archived = 0
        for row in rows:
            record = row_to_record(row, self.memory_type)
            if strength_now(record, now=now) < threshold:
                row.archived_at = now
                row.updated_at = now
                archived += 1
        if archived:
            await self.session.flush()
        return archived

    async def find_by_id_any_table(self, memory_id: str) -> tuple[MemoryRecord, MemoryType] | None:
        row = await self.session.get(self.table, memory_id)
        if row is None:
            return None
        return row_to_record(row, self.memory_type), self.memory_type

    async def list_active_for_learner(self, *, learner_id: str) -> list[MemoryRecord]:
        rows = await self.list_for_learner(
            learner_id=learner_id,
            include_deleted=False,
            include_archived=False,
        )
        return [r for r in rows if r.superseded_by is None]

    async def get_embedding(self, memory_id: str) -> list[float] | None:
        row = await self.session.get(self.table, memory_id)
        if row is None or row.embedding is None:
            return None
        return list(row.embedding)

    async def reinforce(self, memory_id: str, *, learner_id: str, delta: float = 0.05) -> MemoryRecord | None:
        from ..hygiene.decay import reinforce

        row = await self.session.get(self.table, memory_id)
        if row is None or row.learner_id != learner_id or row.deleted_at is not None:
            return None
        record = row_to_record(row, self.memory_type)
        reinforced = reinforce(record, delta=delta)
        self._apply_record(row, reinforced, embedding=None)
        await self.session.flush()
        return row_to_record(row, self.memory_type)

    def _apply_record(
        self,
        row: MemoryColumnsMixin,
        record: MemoryRecord,
        *,
        embedding: list[float] | None,
    ) -> None:
        row.learner_id = record.learner_id
        row.content = record.content
        row.summary = record.summary
        row.tags = record.tags
        if embedding is not None:
            row.embedding = embedding
        row.salience = record.salience
        row.confidence = record.confidence
        row.valence = record.valence
        row.decay_tau_days = record.decay_tau_days
        row.last_accessed_at = record.last_accessed_at
        row.access_count = record.access_count
        row.superseded_by = record.superseded_by
        row.superseded_at = record.superseded_at
        row.provenance = record.provenance.model_dump(mode="json")
        row.kg_node_ids = record.kg_node_ids
        row.created_at = record.created_at
        row.updated_at = record.updated_at
        row.archived_at = record.archived_at
        row.deleted_at = record.deleted_at
        row.expires_at = record.expires_at


def all_persisted_types() -> tuple[MemoryType, ...]:
    return (
        MemoryType.EPISODIC,
        MemoryType.SEMANTIC,
        MemoryType.PROCEDURAL,
        MemoryType.AFFECTIVE,
        MemoryType.CONTEXT,
        MemoryType.REFLECTIVE,
        MemoryType.SOURCE,
    )


def repo_for_type(session: AsyncSession, memory_type: MemoryType) -> TypedMemoryRepository:
    return TypedMemoryRepository(session, memory_type)


async def locate_record(session: AsyncSession, memory_id: str) -> tuple[MemoryRecord, MemoryType] | None:
    for table in MEMORY_TABLES:
        row = await session.get(table, memory_id)
        if row is not None:
            return row_to_record(row, type_for_table(table)), type_for_table(table)
    return None


async def clear_embedding(session: AsyncSession, memory_id: str, memory_type: MemoryType) -> None:
    table = table_for_type(memory_type)
    await session.execute(update(table).where(table.id == memory_id).values(embedding=None))
