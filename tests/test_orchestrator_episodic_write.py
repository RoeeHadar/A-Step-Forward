"""Integration test — orchestrator chat turns persist episodic memories."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from schemas.agents import AgentName, ChatChunk, ChatRequest

from memory_service.default_service import DefaultMemoryService
from memory_service.settings import MemorySettings
from memory_service.stores.database import dispose_engine
from orchestrator.episodic import build_episodic_content, extract_response_text
from orchestrator.runner import OrchestratorRunner
from schemas.memory import MemoryType


def _database_reachable() -> bool:
    url = os.getenv("DATABASE_URL", MemorySettings().database_url)
    if "localhost" not in url and "127.0.0.1" not in url:
        return bool(os.getenv("RUN_MEMORY_STORE_TESTS"))
    return True


async def _postgres_available() -> bool:
    if not _database_reachable():
        return False
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    settings = MemorySettings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        await engine.dispose()


@pytest.fixture
async def postgres_available() -> None:
    if not await _postgres_available():
        pytest.skip("Postgres not available for orchestrator episodic write test")
    await dispose_engine()
    yield
    await dispose_engine()


async def test_chat_turn_writes_episodic_memory_row(postgres_available: None) -> None:
    learner_id = f"learner-{uuid4()}"
    message = "Explain why fractions matter in one sentence."
    memory = DefaultMemoryService()
    runner = OrchestratorRunner(memory_service=memory)

    chunks = await runner.handle(
        ChatRequest(
            learner_id=learner_id,
            message=message,
            requested_agent=AgentName.TUTOR,
        )
    )

    assert any(chunk.kind == "token" and chunk.text for chunk in chunks)

    timeline = await memory.timeline(learner_id=learner_id, k=10)
    episodic = [row for row in timeline if row.type == MemoryType.EPISODIC]

    assert len(episodic) >= 1
    assert message in episodic[0].content
    assert episodic[0].tags == ["chat", AgentName.TUTOR.value]
    assert episodic[0].provenance.kind == "chat"
    assert episodic[0].provenance.agent == AgentName.TUTOR.value


def test_episodic_helpers_format_turn_content() -> None:
    chunks = [
        ChatChunk(kind="token", agent=AgentName.TUTOR, text="Hello"),
        ChatChunk(kind="token", agent=AgentName.TUTOR, text="world"),
    ]
    assert extract_response_text(chunks) == "Hello world"

    content = build_episodic_content(
        user_message="What is 2+2?",
        agent=AgentName.TUTOR,
        response="Let's explore that together.",
    )
    assert "User: What is 2+2?" in content
    assert "Agent (tutor): Let's explore that together." in content
