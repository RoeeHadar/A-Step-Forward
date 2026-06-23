"""In-memory audit store with optional Postgres persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class GatewayAuditRecord:
    id: str
    action: str
    route: str
    learner_id: str | None
    metadata_json: str | None
    created_at: datetime


@dataclass
class AuditStore:
    """Append-only audit buffer. Sub-agent 09 may wire Postgres writes."""

    gateway_events: list[GatewayAuditRecord] = field(default_factory=list)
    _persist_to_db: bool = False

    async def append_gateway_event(
        self,
        *,
        id: str | None = None,
        action: str,
        route: str,
        learner_id: str | None = None,
        metadata_json: str | None = None,
        created_at: datetime | None = None,
    ) -> GatewayAuditRecord:
        record = GatewayAuditRecord(
            id=id or str(uuid4()),
            action=action,
            route=route,
            learner_id=learner_id,
            metadata_json=metadata_json,
            created_at=created_at or datetime.now(timezone.utc),
        )
        self.gateway_events.append(record)
        if self._persist_to_db:
            await self._write_gateway_to_postgres(record)
        return record

    async def list_gateway_events(
        self,
        *,
        limit: int = 100,
        action_prefix: str | None = None,
    ) -> list[GatewayAuditRecord]:
        rows = self.gateway_events
        if action_prefix:
            rows = [r for r in rows if r.action.startswith(action_prefix)]
        return list(reversed(rows[-limit:]))

    async def _write_gateway_to_postgres(self, record: GatewayAuditRecord) -> None:
        try:
            from sqlalchemy import insert

            from ..core.db import session_scope
            from .models import AuditGatewayEvent

            async with session_scope() as session:
                await session.execute(
                    insert(AuditGatewayEvent).values(
                        id=record.id,
                        learner_id=record.learner_id,
                        action=record.action,
                        route=record.route,
                        metadata_json=record.metadata_json,
                        created_at=record.created_at,
                    )
                )
                await session.commit()
        except Exception:
            pass


_store: AuditStore | None = None


def get_audit_store() -> AuditStore:
    global _store
    if _store is None:
        _store = AuditStore()
    return _store
