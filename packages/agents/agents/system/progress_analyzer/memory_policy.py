"""Progress Analyzer memory access policy."""

from __future__ import annotations

from agents.base.memory_policy import MemoryPolicy, MemoryType

MEMORY_POLICY = MemoryPolicy(
    read={MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL},
    write={MemoryType.SEMANTIC, MemoryType.REFLECTIVE},
)
