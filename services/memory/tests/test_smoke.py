"""Phase-0 smoke test for the memory service foundation."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "memory"))

from schemas.common import Provenance
from schemas.memory import MemorySearchInput, MemoryType, MemoryWriteInput

from memory_service.default_service import DefaultMemoryService
from memory_service.settings import MemorySettings


def _database_reachable() -> bool:
    url = os.getenv("DATABASE_URL", MemorySettings().database_url)
    if "localhost" not in url and "127.0.0.1" not in url:
        return bool(os.getenv("RUN_MEMORY_STORE_TESTS"))
    return True


async def main() -> None:
    if not _database_reachable():
        print("skip: Postgres required for memory store smoke test")
        return

    svc = DefaultMemoryService()
    rec = await svc.write(
        MemoryWriteInput(
            learner_id="learner-1",
            type=MemoryType.EPISODIC,
            content="The learner asked for a worked example of long division at 8pm.",
            tags=["math", "long-division"],
            provenance=Provenance(kind="chat", id="turn-1", agent="tutor", model="claude-sonnet-4-5"),
        ),
        agent_id="tutor",
    )
    assert rec.id
    assert rec.salience > 0
    print("write ok:", rec.id, "salience=", round(rec.salience, 3))

    results = await svc.search(
        MemorySearchInput(
            learner_id="learner-1",
            query="long division example",
            agent_id="tutor",
            k=5,
        )
    )
    assert len(results) >= 1
    print("search ok: top score=", round(results[0].score, 3))

    n = await svc.decay_sweep(learner_id="learner-1")
    print("decay_sweep archived:", n)

    report = await svc.dream_now(learner_id="learner-1")
    print("dream_now ok: reviewed=", report.items_reviewed)


if __name__ == "__main__":
    asyncio.run(main())
