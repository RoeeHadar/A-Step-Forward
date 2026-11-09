"""AS-107: CI and Make runners of AS-96/AS-97 guarded scripts handle the opt-in.

- A workflow step that runs a guarded script must have ALLOW_REAL_LLM: "1" on that
  step or its job (an intended real run), never at workflow level.
- Make targets that run a guarded script document the opt-in in `make help` and
  never set it themselves (`make -n` shows no ALLOW_REAL_LLM assignment).
Static checks only: no network, no keys, nothing is executed except `make -n`/`make help`.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
GUARDED = (
    "test-groq|enrich-all-lessons|expand-lessons-substantive|generate-bulk-questions|verify-llm|"
    "run-plan-neon-test|generate-adaptive-lessons|generate-skill-atom-questions|generate-level-bodies|"
    "rag-ingest|rag-eval|seed_diagnostic_items|verify_prod_env"
)
GUARDED_RE = re.compile(rf"(?:^|[\s/])(?:scripts/)?({GUARDED})\.(?:mjs|py)\b")
MAKE_TARGETS = ["enrich-lessons", "enrich-skill-atoms", "enrich-level-bodies", "seed-diagnostic"]


def _guarded_steps() -> list[tuple[str, str, str, dict, dict, dict]]:
    out = []
    for wf_path in sorted((REPO / ".github" / "workflows").glob("*.y*ml")):
        wf = yaml.safe_load(wf_path.read_text(encoding="utf-8")) or {}
        for job_id, job in (wf.get("jobs") or {}).items():
            for i, step in enumerate(job.get("steps") or []):
                hits = GUARDED_RE.findall(step.get("run") or "")
                if hits:
                    out.append(
                        (
                            wf_path.name,
                            job_id,
                            f"{i}:{step.get('name', '')}",
                            wf.get("env") or {},
                            job.get("env") or {},
                            step.get("env") or {},
                        )
                    )
    return out


def test_workflow_steps_running_guarded_scripts_opt_in_locally() -> None:
    steps = _guarded_steps()
    found = {(w, j) for w, j, *_ in steps}
    # The inventory (rg-runners.txt) has exactly these runners; a new one must be reviewed here.
    assert found == {("rag-ingest.yml", "ingest"), ("seed-db.yml", "seed")}, found
    missing = []
    for wf, job, step, wf_env, job_env, step_env in steps:
        assert "ALLOW_REAL_LLM" not in wf_env, (
            f"{wf}: opt-in must be scoped to a job/step, not global"
        )
        if str(step_env.get("ALLOW_REAL_LLM", job_env.get("ALLOW_REAL_LLM"))) != "1":
            missing.append(f"{wf}:{job}:{step}")
    assert not missing, f"guarded script runs without ALLOW_REAL_LLM=1: {missing}"


def _make(*args: str) -> str:
    make = shutil.which("make")
    if not make:
        pytest.skip("make not installed")
    env = {"PATH": "/usr/bin:/bin"}  # no ALLOW_REAL_LLM, no keys
    out = subprocess.run(
        [make, "--no-print-directory", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert out.returncode == 0, out.stderr
    return out.stdout


@pytest.mark.parametrize("target", MAKE_TARGETS)
def test_make_help_documents_opt_in(target: str) -> None:
    lines = [ln for ln in _make("help").splitlines() if re.match(rf"\s*{re.escape(target)}\b", ln)]
    assert lines, f"`make help` does not list {target}"
    block = _make("help")
    start = block.index(lines[0])
    assert "ALLOW_REAL_LLM=1" in block[start : start + 400], (
        f"`make help` does not say {target} needs ALLOW_REAL_LLM=1"
    )


@pytest.mark.parametrize("target", MAKE_TARGETS)
def test_make_never_forces_opt_in(target: str) -> None:
    dry = _make("-n", target)
    assert GUARDED_RE.search(dry), dry
    cmds = [ln for ln in dry.splitlines() if not ln.lstrip().startswith("#")]  # recipe comments
    assert not any("ALLOW_REAL_LLM" in ln for ln in cmds), (
        f"`make -n {target}` sets the opt-in itself:\n{dry}"
    )
    text = (REPO / "Makefile").read_text(encoding="utf-8")
    assert not re.search(r"^\s*(export\s+)?ALLOW_REAL_LLM\s*[:?+]?=", text, re.M)
