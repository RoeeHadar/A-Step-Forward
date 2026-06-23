"""Audit logging for memory R/W and admin actions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class MemoryAuditRecord:
    id: str
    ts: datetime
    action: str
    agent_id: str | None
    learner_id: str | None
    memory_id: str | None
    payload: dict[str, Any]


@dataclass
class MemoryAuditBuffer:
    events: list[MemoryAuditRecord] = field(default_factory=list)

    async def append(
        self,
        action: str,
        *,
        agent_id: str | None = None,
        learner_id: str | None = None,
        memory_id: str | None = None,
        **fields: Any,
    ) -> MemoryAuditRecord:
        record = MemoryAuditRecord(
            id=str(uuid4()),
            ts=datetime.now(timezone.utc),
            action=action,
            agent_id=agent_id,
            learner_id=learner_id,
            memory_id=memory_id,
            payload=fields,
        )
        self.events.append(record)
        logger.info(
            "memory.audit",
            action=action,
            agent_id=agent_id,
            learner_id=learner_id,
            memory_id=memory_id,
            **fields,
        )
        await self._maybe_persist(record)
        return record

    async def list_events(
        self,
        *,
        limit: int = 100,
        learner_id: str | None = None,
    ) -> list[MemoryAuditRecord]:
        rows = self.events
        if learner_id:
            rows = [r for r in rows if r.learner_id == learner_id]
        return list(reversed(rows[-limit:]))

    async def _maybe_persist(self, record: MemoryAuditRecord) -> None:
        try:
            from sqlalchemy import insert

            from ..stores.database import session_scope
            from ..stores.models import AuditMemoryEvent
            from ..settings import MemorySettings

            async with session_scope(MemorySettings()) as session:
                await session.execute(
                    insert(AuditMemoryEvent).values(
                        id=record.id,
                        ts=record.ts,
                        action=record.action,
                        agent_id=record.agent_id,
                        learner_id=record.learner_id,
                        memory_id=record.memory_id,
                        payload=record.payload,
                    )
                )
        except Exception:
            logger.debug("memory.audit.persist_skipped", action=record.action)


_buffer: MemoryAuditBuffer | None = None


def _get_buffer() -> MemoryAuditBuffer:
    global _buffer
    if _buffer is None:
        _buffer = MemoryAuditBuffer()
    return _buffer


async def audit_event(action: str, **fields: Any) -> None:
    agent_id = fields.pop("agent_id", None)
    learner_id = fields.pop("learner_id", None)
    memory_id = fields.pop("memory_id", None)
    await _get_buffer().append(
        action,
        agent_id=agent_id,
        learner_id=learner_id,
        memory_id=memory_id,
        **fields,
    )


async def list_memory_audit_events(
    *,
    limit: int = 100,
    learner_id: str | None = None,
) -> list[dict[str, Any]]:
    rows = await _get_buffer().list_events(limit=limit, learner_id=learner_id)
    return [
        {
            "id": r.id,
            "ts": r.ts.isoformat(),
            "action": r.action,
            "agent_id": r.agent_id,
            "learner_id": r.learner_id,
            "memory_id": r.memory_id,
            "payload": r.payload,
        }
        for r in rows
    ]
