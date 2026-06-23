"""Public API for the Memory Service.

This module is the **only** place feature code should reach for memory R/W. It
composes the stores, hygiene (PII, importance, consolidation, conflict
resolution), retrieval (hybrid + rerank + policy filter), and audit.

The actual implementations live in `stores/`, `hygiene/`, and `retrieval/`.
Sub-agents implementing those modules must keep this surface stable.
"""

from __future__ import annotations

from typing import Protocol

from schemas.memory import (
    MemoryHealthReport,
    MemoryRecord,
    MemorySearchInput,
    MemorySearchResult,
    MemoryUpdateInput,
    MemoryWriteInput,
)

from .settings import MemorySettings


class MemoryService(Protocol):
    """Front-door interface. Implemented by `DefaultMemoryService`."""

    settings: MemorySettings

    async def write(self, input: MemoryWriteInput, *, agent_id: str, child_mode: bool = False) -> MemoryRecord: ...
    async def search(self, input: MemorySearchInput) -> list[MemorySearchResult]: ...
    async def get(self, memory_id: str, *, learner_id: str, agent_id: str) -> MemoryRecord | None: ...
    async def update(self, memory_id: str, patch: MemoryUpdateInput, *, learner_id: str, agent_id: str) -> MemoryRecord: ...
    async def delete(self, memory_id: str, *, learner_id: str, agent_id: str, hard: bool = False) -> None: ...
    async def timeline(self, *, learner_id: str, since: str | None = None, until: str | None = None, k: int = 100) -> list[MemoryRecord]: ...

    # Hygiene operations (usually called by workers, not by request handlers).
    async def dream_now(self, *, learner_id: str) -> MemoryHealthReport: ...
    async def consolidate(self, *, learner_id: str) -> int: ...
    async def decay_sweep(self, *, learner_id: str | None = None) -> int: ...


def get_memory_service() -> MemoryService:
    """DI hook. Sub-agent for 04-memory replaces this with the real implementation."""
    from .default_service import DefaultMemoryService  # local import to avoid heavy import at module load

    return DefaultMemoryService()
