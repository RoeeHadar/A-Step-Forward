"""Curriculum service smoke tests."""

from __future__ import annotations

from pathlib import Path

from schemas.curriculum_seed import load_seed_course

ROOT = Path(__file__).resolve().parents[3]
SEED_DIR = ROOT / "infra" / "seeds" / "courses" / "foundations-of-math"


def test_seed_bundle_validates() -> None:
    bundle = load_seed_course(SEED_DIR)
    assert bundle.course.title == "Foundations of Math"
