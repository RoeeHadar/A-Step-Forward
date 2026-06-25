"""Read-only admin endpoints for audit logs and system stats."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from memory_service.hygiene.audit import list_memory_audit_events

from ..core.audit import log_gateway_audit
from ..core.auth import AuthCtx
from ..core.rbac import require_admin
from ..core.db import get_db
from ..stores import content_store
from ..stores.audit_store import get_audit_store

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/audit/gateway")
async def list_gateway_audit(
    ctx: AuthCtx = Depends(require_admin),
    limit: int = Query(default=100, ge=1, le=500),
    action_prefix: str | None = Query(default=None),
) -> list[dict]:
    await log_gateway_audit(
        action="admin.audit.read",
        route="/v1/admin/audit/gateway",
        learner_id=ctx.learner_id,
        metadata={"limit": limit, "action_prefix": action_prefix},
    )
    store = get_audit_store()
    rows = await store.list_gateway_events(limit=limit, action_prefix=action_prefix)
    return [
        {
            "id": r.id,
            "action": r.action,
            "route": r.route,
            "learner_id": r.learner_id,
            "metadata_json": r.metadata_json,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/audit/memory")
async def list_memory_audit(
    ctx: AuthCtx = Depends(require_admin),
    limit: int = Query(default=100, ge=1, le=500),
    learner_id: str | None = Query(default=None),
) -> list[dict]:
    await log_gateway_audit(
        action="admin.audit.read",
        route="/v1/admin/audit/memory",
        learner_id=ctx.learner_id,
        metadata={"limit": limit, "filter_learner_id": learner_id},
    )
    rows = await list_memory_audit_events(limit=limit, learner_id=learner_id)
    return rows


@router.get("/stats")
async def admin_stats(ctx: AuthCtx = Depends(require_admin)) -> dict:
    await log_gateway_audit(
        action="admin.stats.read",
        route="/v1/admin/stats",
        learner_id=ctx.learner_id,
    )
    gateway_store = get_audit_store()
    memory_rows = await list_memory_audit_events(limit=10_000)
    gateway_rows = await gateway_store.list_gateway_events(limit=10_000)
    return {
        "gateway_audit_event_count": len(gateway_rows),
        "memory_audit_event_count": len(memory_rows),
        "rbac_denial_count": sum(1 for r in gateway_rows if r.action == "rbac.denied"),
    }


@router.get("/content/status")
async def content_status(
    ctx: AuthCtx = Depends(require_admin),
    session=Depends(get_db),
) -> dict:
    await log_gateway_audit(
        action="admin.content.status",
        route="/v1/admin/content/status",
        learner_id=ctx.learner_id,
    )
    return await content_store.get_content_status(session)
