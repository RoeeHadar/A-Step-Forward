"""Dreaming jobs."""

from __future__ import annotations

import asyncio

from ..celery_app import app


@app.task(name="workers.jobs.dreaming.dream_learner")
def dream_learner(learner_id: str) -> dict:
    from memory_service.api import get_memory_service

    svc = get_memory_service()
    report = asyncio.run(svc.dream_now(learner_id=learner_id))
    return report.model_dump()


@app.task(name="workers.jobs.dreaming.dream_all_active")
def dream_all_active() -> int:
    # Sub-agent 09-infra: query the learners table for active learners and
    # fan out to `dream_learner.delay(learner_id)` per row. Phase-0 returns 0.
    return 0
