"""Eval runner for memory hygiene YAML suites (offline, no DB)."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "memory"))

from schemas.common import Provenance
from schemas.memory import MemoryRecord, MemoryType

from memory_service.hygiene.conflict_resolution import resolve_conflicts
from memory_service.hygiene.consolidation import find_near_duplicates
from memory_service.hygiene.decay import strength_now
from memory_service.hygiene.pii import redact
from memory_service.hygiene.text_similarity import jaccard_similarity


class InMemoryRepo:
    def __init__(self) -> None:
        self.rows: dict[str, MemoryRecord] = {}

    async def upsert(self, record: MemoryRecord, *, embedding: list[float] | None = None) -> MemoryRecord:
        self.rows[record.id] = record
        return record

    async def list_by_types(self, learner_id: str, types: set[MemoryType]) -> list[MemoryRecord]:
        return [r for r in self.rows.values() if r.learner_id == learner_id and r.type in types]


def _record(content: str) -> MemoryRecord:
    return MemoryRecord(
        id=str(uuid4()),
        learner_id="eval-learner",
        type=MemoryType.SEMANTIC,
        content=content,
        provenance=Provenance(kind="system", id="eval", agent="eval", model="none"),
    )


async def run_pii_eval(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for case in data["cases"]:
        cleaned = await redact(case["input"])
        for forbidden in case.get("must_not_contain", []):
            if forbidden in cleaned:
                return False
        for required in case.get("must_contain", []):
            if required not in cleaned:
                return False
    return True


async def run_conflict_eval(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for case in data["cases"]:
        repo = InMemoryRepo()
        existing = _record(case["existing"])
        await repo.upsert(existing)
        incoming = _record(case["incoming"])
        incoming.confidence = 0.9
        conflict = await resolve_conflicts(repo, incoming)
        superseded = existing.superseded_by or incoming.superseded_by
        if case["expect_supersession"] and not superseded:
            return False
        if not case["expect_supersession"] and superseded:
            return False
    return True


async def run_consolidation_eval(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for case in data["cases"]:
        repo = InMemoryRepo()
        a = _record(case["a"])
        b = _record(case["b"])
        await repo.upsert(a)
        await repo.upsert(b)
        sim = jaccard_similarity(a.content, b.content)
        dups = await find_near_duplicates(repo, learner_id="eval-learner", cosine=case["min_similarity"])
        merged = len(dups) >= 1
        if case["expect_merge"] and not merged:
            return False
        if not case["expect_merge"] and merged and sim >= case["min_similarity"]:
            return False
    return True


async def run_decay_eval(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    for case in data["cases"]:
        record = _record("decay probe")
        record.salience = case["salience"]
        record.last_accessed_at = now - timedelta(days=case["age_days"])
        s = strength_now(record, now=now)
        if "min_strength" in case and s < case["min_strength"]:
            return False
        if "max_strength" in case and s > case["max_strength"]:
            return False
        if case.get("below_archive_threshold") and s >= case["below_archive_threshold"]:
            return False
    return True


async def main() -> int:
    root = ROOT / "evals" / "memory"
    suites = [
        (root / "pii" / "redaction.yaml", run_pii_eval),
        (root / "conflict" / "contradictions.yaml", run_conflict_eval),
        (root / "consolidation" / "merge.yaml", run_consolidation_eval),
        (root / "decay" / "archive.yaml", run_decay_eval),
    ]
    ok = True
    for path, runner in suites:
        passed = await runner(path)
        print(f"{path.name}: {'PASS' if passed else 'FAIL'}")
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
