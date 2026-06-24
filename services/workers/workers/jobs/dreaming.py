"""Dreaming jobs."""

from __future__ import annotations

import argparse
import asyncio
import sys

import structlog

from ..celery_app import app
from .run_util import is_dry_run, log_dry_run

logger = structlog.get_logger(__name__)


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


def run_dreaming(*, dry_run: bool) -> int:
    """Entry point for GitHub Actions cron and local CLI."""
    if dry_run:
        log_dry_run(
            "dream_all_active",
            schedule="nightly 03:00 UTC",
            action="query active learners and run dream_now per learner",
            would_fan_out="dream_learner.delay(learner_id)",
        )
        return 0

    count = dream_all_active()
    logger.info("dream_all_active_complete", learners_processed=count)
    return count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the nightly dreaming (Memory Steward) job.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log planned actions without writing (also default when DATABASE_URL is unset).",
    )
    args = parser.parse_args(argv)
    dry_run = is_dry_run(flag=args.dry_run)
    if dry_run and not args.dry_run:
        logger.info("dry_run_auto", reason="DATABASE_URL unset")

    exit_code = 0 if run_dreaming(dry_run=dry_run) >= 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
