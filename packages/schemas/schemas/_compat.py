"""Tiny compatibility shim.

The project requires Python 3.11+ at runtime (see pyproject.toml), but during
Phase 0 we still want a one-shot smoke test to work on older interpreters.
Importing from this module lets sub-agents drop the shim later without
changing call sites.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:  # pragma: no cover — Python 3.10 fallback for local Phase-0 smoke tests
    from enum import Enum

    class StrEnum(str, Enum):  # type: ignore[no-redef]
        """Back-compat StrEnum for Python <3.11."""

        def __str__(self) -> str:  # pragma: no cover
            return self.value


__all__ = ["StrEnum"]
