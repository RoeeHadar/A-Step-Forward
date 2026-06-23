"""Memory access policy helpers for agents."""

from __future__ import annotations

from schemas.memory import MemoryAccessPolicy, MemoryType

# Re-export for agent modules (see skills/build-an-agent/SKILL.md).
MemoryPolicy = MemoryAccessPolicy

__all__ = ["MemoryPolicy", "MemoryType", "MemoryAccessPolicy"]
