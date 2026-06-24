"""Fetches and formats the top-k memories for a learner to inject into the system prompt."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HydratedMemory:
    summary: str  # formatted block ready to inject into system prompt
    record_ids: list[str] = field(default_factory=list)  # for citation / pinning


async def hydrate(
    *,
    learner_id: str,
    query: str,
    k: int = 8,
    memory_api=None,  # injected; None = graceful skip
) -> HydratedMemory:
    """Return a formatted block of the learner's most relevant memories.

    If memory_api is None (no DB configured) returns an empty HydratedMemory
    so agents degrade gracefully in dev/offline mode.
    """
    if memory_api is None:
        return HydratedMemory(summary="", record_ids=[])
    try:
        from schemas.memory import MemorySearchInput

        results = await memory_api.search(
            MemorySearchInput(
                learner_id=learner_id,
                query=query,
                k=k,
                min_strength=0.15,
            )
        )
        if not results:
            return HydratedMemory(summary="", record_ids=[])
        lines = ["## What you know about this learner"]
        for r in results:
            rec = r.record
            lines.append(f"- [{rec.type}] {rec.content} (strength={r.score:.2f})")
        return HydratedMemory(
            summary="\n".join(lines),
            record_ids=[r.record.id for r in results],
        )
    except Exception:  # noqa: BLE001
        return HydratedMemory(summary="", record_ids=[])
