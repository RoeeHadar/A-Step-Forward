"""Celery app + beat schedule.

Phase 0 ships the schedule (dreamer nightly, decay every 6h, KG verify daily)
so the operational shape is locked in. Sub-agent 09-infra connects this to
real brokers + worker pools.
"""

from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

broker = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

app = Celery("asf", broker=broker, backend=backend, include=["workers.jobs.dreaming", "workers.jobs.decay", "workers.jobs.kg_ingest"])

app.conf.timezone = "UTC"
app.conf.task_default_queue = "default"
app.conf.beat_schedule = {
    "dream-nightly": {
        "task": "workers.jobs.dreaming.dream_all_active",
        "schedule": crontab(hour=3, minute=0),
    },
    "decay-sweep-6h": {
        "task": "workers.jobs.decay.decay_sweep_all",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "kg-verify-daily": {
        "task": "workers.jobs.kg_ingest.verify_recent",
        "schedule": crontab(hour=4, minute=30),
    },
}
