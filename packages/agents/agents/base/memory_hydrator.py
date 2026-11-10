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
    agent_id: str | None = None,
) -> HydratedMemory:
    """Return a formatted block of the learner's most relevant memories.

    If memory_api is None (no DB configured) returns an empty HydratedMemory
    so agents degrade gracefully in dev/offline mode.

    AS-114: memory reads are policy-filtered per agent, and a search needs the
    reading agent's id. Without one, no memories are returned. This is the
    pre-AS-90 behaviour (3b7d2774): there MemorySearchInput.agent_id was required,
    this call never passed it, the ValidationError was swallowed below and the
    search was never reached. After AS-90 the field defaults to None and the
    search ran under the default read policy. When a caller passes agent_id, the
    search goes through MemorySearchBody, which applies the pre-AS-90 checks.
    """
    if memory_api is None or not agent_id:
        return HydratedMemory(summary="", record_ids=[])
    try:
        from schemas.memory import MemorySearchBody

        results = await memory_api.search(
            MemorySearchBody(
                learner_id=learner_id,
                query=query,
                k=k,
                min_strength=0.15,
                agent_id=agent_id,
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
    except Exception:
        return HydratedMemory(summary="", record_ids=[])
