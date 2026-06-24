"""Fire-and-forget persistence for lightweight memory_events rows."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from sqlalchemy import insert

from .settings import MemorySettings
from .stores.database import session_scope
from .stores.models import MemoryEvent

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

_MAX_CONTENT_LEN = 20_000


def database_url_configured() -> bool:
    """True when DATABASE_URL is explicitly set in the environment."""
    return bool(os.environ.get("DATABASE_URL", "").strip())


async def write_memory_event(
    session: AsyncSession,
    *,
    learner_id: str,
    agent: str,
    content: str,
    event_type: str = "chat_turn",
) -> None:
    """Insert one row into memory_events using the provided async session."""
    trimmed = content if len(content) <= _MAX_CONTENT_LEN else content[: _MAX_CONTENT_LEN - 3] + "..."
    await session.execute(
        insert(MemoryEvent).values(
            learner_id=learner_id,
            agent=agent,
            content=trimmed,
            event_type=event_type,
        )
    )


async def persist_memory_event(
    *,
    learner_id: str,
    agent: str,
    content: str,
    event_type: str = "chat_turn",
) -> None:
    """Persist a memory event; skips gracefully when DATABASE_URL is unset."""
    if not database_url_configured():
        logger.warning("DATABASE_URL not set; skipping memory event write")
        return

    try:
        settings = MemorySettings()
        async with session_scope(settings) as session:
            await write_memory_event(
                session,
                learner_id=learner_id,
                agent=agent,
                content=content,
                event_type=event_type,
            )
    except Exception:
        logger.exception(
            "memory.event_write_failed",
            extra={"learner_id": learner_id, "agent": agent, "event_type": event_type},
        )
