"""Decay sweep jobs."""

from __future__ import annotations

import argparse
import asyncio
import sys

import structlog

from ..celery_app import app
from .run_util import is_dry_run, log_dry_run

logger = structlog.get_logger(__name__)


@app.task(name="workers.jobs.decay.decay_sweep_all")
def decay_sweep_all() -> int:
    from memory_service.api import get_memory_service

    svc = get_memory_service()
    return asyncio.run(svc.decay_sweep(learner_id=None))


def run_decay(*, dry_run: bool) -> int:
    """Entry point for GitHub Actions cron and local CLI."""
    if dry_run:
        log_dry_run(
            "decay_sweep_all",
            schedule="weekly Sun 04:00 UTC",
            action="run decay_sweep for all learners",
            learner_id=None,
        )
        return 0

    count = decay_sweep_all()
    logger.info("decay_sweep_all_complete", memories_archived=count)
    return count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the weekly memory decay sweep job.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log planned actions without writing (also default when DATABASE_URL is unset).",
    )
    args = parser.parse_args(argv)
    dry_run = is_dry_run(flag=args.dry_run)
    if dry_run and not args.dry_run:
        logger.info("dry_run_auto", reason="DATABASE_URL unset")

    exit_code = 0 if run_decay(dry_run=dry_run) >= 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
