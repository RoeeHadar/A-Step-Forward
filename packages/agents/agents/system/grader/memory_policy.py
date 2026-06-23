"""Grader memory access policy."""

from __future__ import annotations

from agents.base.memory_policy import MemoryPolicy, MemoryType

MEMORY_POLICY = MemoryPolicy(
    read={MemoryType.SEMANTIC, MemoryType.PROCEDURAL},
    write={MemoryType.EPISODIC, MemoryType.REFLECTIVE},
)
