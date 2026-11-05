"""AS-90 runtime guard: fail the session if production code reads an
attribute that FlexibleModel serves through its ``__getattr__`` fallback
(i.e. a field that is not declared in ``model_fields``).

Test-only: wraps ``FlexibleModel.__getattr__`` while pytest runs; production
behaviour is unchanged. Reads made from test files are ignored. Set
``FLEXIBLE_FALLBACK_REPORT=<path>`` to also write the hits to a file.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
_HITS: Counter[tuple[str, str, str]] = Counter()


def _is_production(filename: str) -> bool:
    try:
        rel = Path(filename).resolve().relative_to(_ROOT)
    except ValueError:
        return False
    parts = rel.parts
    if not parts or parts[0] in {".venv", "tests", "node_modules"} or "tests" in parts:
        return False
    name = rel.name
    return (
        name.endswith(".py")
        and not name.startswith("test_")
        and name != "conftest.py"
        and rel.parts[-2:] != ("schemas", "_dynamic.py")
    )


def _install() -> None:
    try:
        from schemas._dynamic import FlexibleModel
    except Exception:  # schemas not importable in this run
        return
    if getattr(FlexibleModel.__getattr__, "_as90_spy", False):
        return
    original = FlexibleModel.__getattr__

    def spy(self: FlexibleModel, item: str) -> object:
        if not item.startswith("_"):
            frame = sys._getframe(1)
            if _is_production(frame.f_code.co_filename):
                rel = Path(frame.f_code.co_filename).resolve().relative_to(_ROOT)
                _HITS[(type(self).__name__, item, f"{rel}:{frame.f_lineno}")] += 1
        return original(self, item)

    spy._as90_spy = True  # type: ignore[attr-defined]
    FlexibleModel.__getattr__ = spy  # type: ignore[method-assign]


_install()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if not _HITS:
        return
    lines = [f"{c}.{f} {loc} x{n}" for (c, f, loc), n in sorted(_HITS.items())]
    report = os.environ.get("FLEXIBLE_FALLBACK_REPORT")
    if report:
        Path(report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stderr.write(
        "\nAS-90 FlexibleModel fallback reads from production code (undeclared fields):\n  "
        + "\n  ".join(lines)
        + "\n"
    )
    session.exitstatus = pytest.ExitCode.TESTS_FAILED
