"""Gateway audit logging — memory of RBAC denials, admin actions, model overrides."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog

from ..stores.audit_store import get_audit_store

logger = structlog.get_logger(__name__)


async def log_gateway_audit(
    *,
    action: str,
    route: str,
    learner_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    payload = {
        "id": str(uuid4()),
        "action": action,
        "route": route,
        "learner_id": learner_id,
        "metadata_json": json.dumps(metadata or {}, default=str),
        "created_at": datetime.now(timezone.utc),
    }
    store = get_audit_store()
    await store.append_gateway_event(**payload)
    logger.info("gateway.audit", **{k: v for k, v in payload.items() if k != "metadata_json"})
