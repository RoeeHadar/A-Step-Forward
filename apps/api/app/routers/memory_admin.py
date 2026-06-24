"""Memory admin endpoints — dream trigger, consolidation, decay sweep."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from ..core.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin", tags=["memory-admin"])


def _check_admin_key(x_admin_key: str | None, settings) -> None:
    """Raise 403 if admin key is configured and doesn't match."""
    configured = getattr(settings, "admin_key", "")
    if configured and x_admin_key != configured:
        raise HTTPException(status_code=403, detail="Invalid admin key")


class DreamResponse(BaseModel):
    learner_id: str
    items_reviewed: int
    items_promoted: int
    items_archived: int
    items_merged: int


@router.post("/dream")
async def trigger_dream(
    learner_id: str = Query(..., description="Learner ID to run dreaming for"),
    window_hours: int = Query(24, ge=1, le=168),
    x_admin_key: Annotated[str | None, Header()] = None,
) -> DreamResponse:
    """Trigger a dreaming pass for a learner. Requires X-Admin-Key header if admin_key is set."""
    settings = get_settings()
    _check_admin_key(x_admin_key, settings)

    try:
        from memory_service.api import get_memory_service
        from memory_service.hygiene.dreaming import dream
        from memory_service.stores.repository import MemoryRepository

        svc = get_memory_service()
        repo = MemoryRepository(svc.settings)
        report = await dream(
            repo,
            learner_id=learner_id,
            window_hours=window_hours,
            consolidation_cosine=0.85,
            archive_threshold=0.05,
            settings=svc.settings,
        )
        return DreamResponse(
            learner_id=report.learner_id,
            items_reviewed=report.items_reviewed,
            items_promoted=report.items_promoted,
            items_archived=report.items_archived,
            items_merged=report.items_merged,
        )
    except Exception as exc:
        logger.exception("dream endpoint failed for learner=%s", learner_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
