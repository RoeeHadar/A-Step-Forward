"""AS-98: learning_path, memory and graphrag declare the `agents` workspace package.

AS-93 moved quiz_generator.generate_via_llm, memory hygiene.llm_helper.dream_llm_complete and
graphrag ingest.Extractor onto a lazy ``from agents.base.llm import ...``. Without a declared
dependency a service installed on its own silently falls back (stub quiz, "" dream) or raises
ImportError (extractor). These checks are static (pyproject/uv.lock parsing) plus an offline
``uv lock --check`` when uv is on PATH. No network, no keys.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SERVICES = {
    "learning-path-service": "services/learning_path",
    "memory-service": "services/memory",
    "graphrag-service": "services/graphrag",
}


def _dep_names(deps: list[str]) -> set[str]:
    return {re.split(r"[\s\[<>=!~;]", d.strip(), maxsplit=1)[0].lower() for d in deps}


def _lock_packages() -> dict[str, dict]:
    lock = tomllib.loads((REPO / "uv.lock").read_text(encoding="utf-8"))
    return {p["name"]: p for p in lock["package"]}


@pytest.mark.parametrize("name", sorted(SERVICES))
def test_pyproject_declares_agents_workspace_dep(name: str) -> None:
    py = tomllib.loads((REPO / SERVICES[name] / "pyproject.toml").read_text(encoding="utf-8"))
    assert py["project"]["name"] == name
    assert "agents" in _dep_names(py["project"]["dependencies"])
    assert py["tool"]["uv"]["sources"].get("agents") == {"workspace": True}


@pytest.mark.parametrize("name", sorted(SERVICES))
def test_uv_lock_records_agents_dep(name: str) -> None:
    pkg = _lock_packages()[name]
    assert {"name": "agents"} in pkg["dependencies"]
    assert {"name": "agents", "editable": "packages/agents"} in pkg["metadata"]["requires-dist"]


def test_agents_does_not_depend_on_these_services() -> None:
    agents = _lock_packages()["agents"]
    names = {d["name"] for d in agents.get("dependencies", [])}
    assert not names & set(SERVICES), "agents -> service dependency would create a cycle"


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not on PATH")
def test_uv_lock_is_current_offline() -> None:
    proc = subprocess.run(
        ["uv", "lock", "--offline", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
