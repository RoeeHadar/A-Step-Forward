"""Tutor memory access policy."""

from __future__ import annotations

from agents.base.memory_policy import MemoryPolicy, MemoryType

MEMORY_POLICY = MemoryPolicy(
    read={MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.PROCEDURAL, MemoryType.REFLECTIVE},
    write={MemoryType.EPISODIC, MemoryType.REFLECTIVE},
)
