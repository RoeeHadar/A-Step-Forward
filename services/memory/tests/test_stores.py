"""Integration tests for Postgres-backed memory stores."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "memory"))

import pytest
from schemas.common import Provenance
from schemas.memory import MemoryRecord, MemoryType, MemoryUpdateInput

from memory_service.settings import MemorySettings
from memory_service.stores.database import dispose_engine, session_scope
from memory_service.stores.repository import MemoryRepository
from memory_service.stores.type_repositories import all_persisted_types, repo_for_type


def _database_reachable() -> bool:
    url = os.getenv("DATABASE_URL", MemorySettings().database_url)
    if "localhost" not in url and "127.0.0.1" not in url:
        return bool(os.getenv("RUN_MEMORY_STORE_TESTS"))
    return True


pytestmark = pytest.mark.skipif(not _database_reachable(), reason="Postgres not configured for store tests")


@pytest.fixture
async def repo() -> MemoryRepository:
    await dispose_engine()
    settings = MemorySettings()
    repository = MemoryRepository(settings)
    yield repository
    await dispose_engine()


def _sample_record(*, learner_id: str, memory_type: MemoryType, content: str) -> MemoryRecord:
    return MemoryRecord(
        id=str(uuid4()),
        learner_id=learner_id,
        type=memory_type,
        content=content,
        tags=["test"],
        provenance=Provenance(kind="system", id="test", agent="pytest", model="none"),
    )


@pytest.mark.parametrize("memory_type", list(all_persisted_types()))
async def test_upsert_and_get_per_type(repo: MemoryRepository, memory_type: MemoryType) -> None:
    learner_id = f"learner-{uuid4()}"
    record = _sample_record(
        learner_id=learner_id,
        memory_type=memory_type,
        content=f"Stored memory for {memory_type.value}",
    )
    saved = await repo.upsert(record)
    assert saved.id == record.id
    assert saved.type == memory_type

    fetched = await repo.get(record.id, learner_id=learner_id)
    assert fetched is not None
    assert fetched.content == record.content
    assert fetched.tags == ["test"]


async def test_patch_updates_content(repo: MemoryRepository) -> None:
    learner_id = f"learner-{uuid4()}"
    record = _sample_record(
        learner_id=learner_id,
        memory_type=MemoryType.SEMANTIC,
        content="Learner prefers visual explanations.",
    )
    await repo.upsert(record)
    updated = await repo.patch(
        record.id,
        learner_id=learner_id,
        patch=MemoryUpdateInput(content="Learner prefers worked examples.", reason="learner correction"),
    )
    assert updated.content == "Learner prefers worked examples."


async def test_soft_delete_hides_record(repo: MemoryRepository) -> None:
    learner_id = f"learner-{uuid4()}"
    record = _sample_record(
        learner_id=learner_id,
        memory_type=MemoryType.EPISODIC,
        content="Temporary session note.",
    )
    await repo.upsert(record)
    await repo.delete(record.id, learner_id=learner_id, hard=False)
    assert await repo.get(record.id, learner_id=learner_id) is None


async def test_timeline_orders_by_created_at(repo: MemoryRepository) -> None:
    learner_id = f"learner-{uuid4()}"
    first = _sample_record(learner_id=learner_id, memory_type=MemoryType.EPISODIC, content="first")
    second = _sample_record(learner_id=learner_id, memory_type=MemoryType.SEMANTIC, content="second")
    await repo.upsert(first)
    await repo.upsert(second)
    timeline = await repo.timeline(learner_id=learner_id, k=10)
    assert len(timeline) >= 2
    assert timeline[0].created_at >= timeline[1].created_at


async def test_working_memory_rejected(repo: MemoryRepository) -> None:
    record = _sample_record(
        learner_id=f"learner-{uuid4()}",
        memory_type=MemoryType.WORKING,
        content="ephemeral",
    )
    with pytest.raises(ValueError, match="ephemeral"):
        await repo.upsert(record)


async def test_set_embedding(repo: MemoryRepository) -> None:
    settings = MemorySettings()
    learner_id = f"learner-{uuid4()}"
    record = _sample_record(
        learner_id=learner_id,
        memory_type=MemoryType.SEMANTIC,
        content="Embedding target memory.",
    )
    await repo.upsert(record)
    embedding = [0.1] * settings.embedding_dim
    await repo.set_embedding(record.id, MemoryType.SEMANTIC, embedding)

    async with session_scope(settings) as session:
        typed = repo_for_type(session, MemoryType.SEMANTIC)
        row = await typed.get(record.id, learner_id=learner_id)
        assert row is not None
