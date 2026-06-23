"""Memory access policy for the orchestrator."""

from __future__ import annotations

from agents.base.memory_policy import MemoryPolicy, MemoryType

MEMORY_POLICY = MemoryPolicy(read=set(MemoryType), write=set())
