"""Shared helpers for cron job CLI entry points."""

from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def is_dry_run(*, flag: bool) -> bool:
    """True when --dry-run is passed or DATABASE_URL is unset."""
    return flag or not os.getenv("DATABASE_URL", "").strip()


def log_dry_run(job: str, **details: Any) -> None:
    logger.info("dry_run", job=job, writes=False, **details)
