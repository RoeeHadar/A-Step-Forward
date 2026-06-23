"""Decay sweep jobs."""

from __future__ import annotations

import asyncio

from ..celery_app import app


@app.task(name="workers.jobs.decay.decay_sweep_all")
def decay_sweep_all() -> int:
    from memory_service.api import get_memory_service

    svc = get_memory_service()
    return asyncio.run(svc.decay_sweep(learner_id=None))
