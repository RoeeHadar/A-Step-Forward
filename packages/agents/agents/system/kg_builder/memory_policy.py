"""KG Builder memory access policy."""

from __future__ import annotations

from agents.base.memory_policy import MemoryPolicy, MemoryType

MEMORY_POLICY = MemoryPolicy(
    read={MemoryType.SOURCE},
    write={MemoryType.SOURCE},
)
