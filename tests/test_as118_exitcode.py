"""AS-118: the root conftest's AS-90 FlexibleModel fallback reporter must not
change pytest's exit code.

Each case runs an isolated inner pytest session in a subprocess (no network, no
DB). The session's rootdir holds a copy of the repo's root conftest.py and a
"production" module that reads an undeclared FlexibleModel field, so the
reporter's fallback path is really hit. Expected: hits + all tests passing -> rc 0
(rc 1 before AS-118); hits + a failing test -> rc 1. In both cases the reporter
text is still written.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_HEADER = "AS-90 FlexibleModel fallback reads from production code (undeclared fields):"

_PROD = """from schemas._dynamic import FlexibleModel


class Thing(FlexibleModel):
    name: str | None = None


def read_undeclared():
    return Thing(name="x").undeclared_field
"""


def _run(tmp_path: Path, test_body: str) -> subprocess.CompletedProcess[str]:
    shutil.copy(_ROOT / "conftest.py", tmp_path / "conftest.py")
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / "prod_mod.py").write_text(_PROD, encoding="utf-8")
    (tmp_path / "test_inner.py").write_text(
        "from prod_mod import read_undeclared\n\n\n" + test_body, encoding="utf-8"
    )
    env = {k: v for k, v in os.environ.items() if k not in {"PYTEST_ADDOPTS", "AS114_OBS"}}
    env["PYTHONPATH"] = os.pathsep.join([str(tmp_path), str(_ROOT / "packages" / "schemas")])
    env["FLEXIBLE_FALLBACK_REPORT"] = str(tmp_path / "hits.txt")
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(tmp_path)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _assert_reported(proc: subprocess.CompletedProcess[str], tmp_path: Path) -> None:
    assert _HEADER in proc.stderr, proc.stdout + proc.stderr
    assert "Thing.undeclared_field prod_mod.py:9 x1" in proc.stderr
    assert (tmp_path / "hits.txt").read_text(encoding="utf-8") == (
        "Thing.undeclared_field prod_mod.py:9 x1\n"
    )


def test_fallback_hit_with_all_tests_passing_exits_0(tmp_path: Path) -> None:
    proc = _run(tmp_path, "def test_ok():\n    assert read_undeclared() is None\n")
    _assert_reported(proc, tmp_path)
    assert "1 passed" in proc.stdout
    assert proc.returncode == pytest.ExitCode.OK, proc.stdout + proc.stderr


def test_fallback_hit_with_a_failing_test_exits_1(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        "def test_ok():\n    assert read_undeclared() is None\n\n\n"
        "def test_seeded_failure():\n    assert False, 'AS-118 seeded failure'\n",
    )
    _assert_reported(proc, tmp_path)
    assert "1 failed, 1 passed" in proc.stdout
    assert proc.returncode == pytest.ExitCode.TESTS_FAILED, proc.stdout + proc.stderr
