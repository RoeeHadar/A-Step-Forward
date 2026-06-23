"""Child-mode write restrictions for memory service."""

from __future__ import annotations

from schemas.errors import PolicyViolation
from schemas.memory import MemoryType

COPPA_AGE_THRESHOLD = 13


def resolve_child_mode(*, age: int | None, child_mode_flag: bool) -> bool:
    if child_mode_flag:
        return True
    return age is not None and age < COPPA_AGE_THRESHOLD


def assert_affective_allowed(memory_type: MemoryType, *, child_mode: bool) -> None:
    """COPPA: no affective-memory persistence in child mode."""
    if child_mode and memory_type == MemoryType.AFFECTIVE:
        raise PolicyViolation("affective memory writes are disabled in child mode")
