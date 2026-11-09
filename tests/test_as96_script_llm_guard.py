"""AS-96: scripts that call a real LLM refuse to run without ALLOW_REAL_LLM=1.

Fakes only. Each script runs as a child process in a scratch copy of the
files it needs (so a script that is not guarded can't touch the repo), under
`unshare -rn` (no network), with placeholder keys and ALLOW_REAL_LLM/EVAL_REAL
unset.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PLACEHOLDER_KEY = "placeholder-not-a-real-key"

# (path from repo root, args). Each one calls Groq when it runs for real.
GUARDED_SCRIPTS = [
    ("test-groq.mjs", []),
    ("scripts/enrich-all-lessons.mjs", []),
    ("scripts/expand-lessons-substantive.mjs", []),
    ("scripts/generate-adaptive-lessons.mjs", []),
    ("scripts/generate-bulk-questions.mjs", []),
    ("scripts/generate-level-bodies.mjs", []),
    ("scripts/generate-skill-atom-questions.mjs", []),
    ("apps/web/scripts/verify-llm.mjs", []),
    ("apps/web/scripts/run-plan-neon-test.mjs", []),
    ("scripts/seed_diagnostic_items.py", ["--dry-run"]),
    ("scripts/verify_prod_env.py", []),
]

TLS_FILES = [
    "test-groq.mjs",
    "scripts/enrich-all-lessons.mjs",
    "scripts/generate-level-bodies.mjs",
    # AS-125: the seed scripts' usage comments advised NODE_TLS_REJECT_UNAUTHORIZED='0' (AS-121).
    "scripts/seed-pilot-demo.mjs",
    "scripts/seed-cohort-pilot.mjs",
]
# AS-125: repo-wide, the only tracked files allowed to name the variable are the tests that
# assert its absence.
TLS_NAME_ALLOWED = {
    "tests/test_as96_script_llm_guard.py",
    "tests/test_as108_embedder_tls.py",
}


def _no_net_prefix() -> list[str]:
    unshare = shutil.which("unshare")
    assert unshare, "unshare is required so a script that is not guarded cannot reach the network"
    probe = subprocess.run([unshare, "-rn", "true"], capture_output=True)
    assert probe.returncode == 0, f"unshare -rn unavailable: {probe.stderr!r}"
    return [unshare, "-rn"]


def _sandbox(tmp_path: Path, rel: str) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(REPO / "scripts" / "lib", root / "scripts" / "lib")
    py_guard = REPO / "scripts" / "llm_script_guard.py"
    if py_guard.exists():
        shutil.copy2(py_guard, root / "scripts" / py_guard.name)
    (root / "node_modules").symlink_to(REPO / "node_modules")
    dst = root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / rel, dst)
    return root


def _env(tmp_path: Path, **extra: str) -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "PYTHONPATH": os.pathsep.join(p for p in sys.path if p),
        "GROQ_API_KEY": PLACEHOLDER_KEY,
        "LLM_API_KEY": PLACEHOLDER_KEY,
    }
    env.update(extra)  # ALLOW_REAL_LLM/EVAL_REAL are only present if a test passes them
    return env


def _run(cmd: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        _no_net_prefix() + cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=90
    )


@pytest.mark.parametrize(("rel", "args"), GUARDED_SCRIPTS, ids=[r for r, _ in GUARDED_SCRIPTS])
def test_script_refuses_without_opt_in(tmp_path: Path, rel: str, args: list[str]) -> None:
    root = _sandbox(tmp_path, rel)
    exe = sys.executable if rel.endswith(".py") else "node"
    out = _run([exe, str(root / rel), *args], cwd=root, env=_env(tmp_path))
    assert out.returncode == 3, (out.returncode, out.stdout[-800:], out.stderr[-800:])
    assert "[llm-guard]" in out.stderr and "ALLOW_REAL_LLM=1" in out.stderr, out.stderr[-800:]
    assert PLACEHOLDER_KEY not in out.stdout + out.stderr


_GROQ_CLIENT_PROBE = r"""
const calls = [];
globalThis.fetch = async (url, init) => {
  calls.push(String(url));
  const body = { choices: [{ message: { content: '{"ok":1}' } }] };
  return { ok: true, status: 200, json: async () => body, text: async () => '' };
};
const m = await import(process.argv[1]);
let result = null, error = null;
const msgs = [{ role: 'user', content: 'hi' }];
try { result = await m.callGroq(msgs, { maxRetries: 1, timeoutMs: 1000 }); }
catch (e) { error = { name: e.name, message: e.message }; }
console.log(JSON.stringify({ calls, result, error }));
"""


def _probe_groq_client(tmp_path: Path, **extra: str) -> dict:
    root = _sandbox(tmp_path, "scripts/lib/groq-client.mjs")
    lib = root / "scripts" / "lib" / "groq-client.mjs"
    out = _run(
        ["node", "--input-type=module", "-e", _GROQ_CLIENT_PROBE, lib.as_uri()],
        cwd=root,
        env=_env(tmp_path, **extra),
    )
    assert out.returncode == 0, out.stderr[-800:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_groq_client_lib_refuses_without_opt_in_and_fetches_with_it(tmp_path: Path) -> None:
    refused = _probe_groq_client(tmp_path / "a")
    assert refused["calls"] == [], refused
    assert refused["error"] and refused["error"]["name"] == "LlmScriptGuardError", refused
    assert "ALLOW_REAL_LLM=1" in refused["error"]["message"]

    # With the explicit opt-in the fake fetch is reached (once), so the guard is the only gate.
    allowed = _probe_groq_client(tmp_path / "b", ALLOW_REAL_LLM="1")
    assert allowed["error"] is None and len(allowed["calls"]) == 1, allowed


def test_guard_helpers_accept_only_explicit_opt_in(tmp_path: Path) -> None:
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from llm_script_guard import LLM_GUARD_EXIT_CODE, real_llm_allowed
    finally:
        sys.path.pop(0)
    assert LLM_GUARD_EXIT_CODE == 3
    assert real_llm_allowed({"ALLOW_REAL_LLM": "1"})
    for v in (None, "", "0", "true", "yes", "2"):
        assert not real_llm_allowed({} if v is None else {"ALLOW_REAL_LLM": v}), v

    probe = (
        "const m = await import(process.argv[1]);"
        "const vals = ['1', '', '0', 'true', 'yes'];"
        "const got = vals.map((v) => m.realLlmAllowed({ ALLOW_REAL_LLM: v }));"
        "console.log(JSON.stringify(got.concat([m.realLlmAllowed({}), m.LLM_GUARD_EXIT_CODE])));"
    )
    out = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            probe,
            (REPO / "scripts/lib/llm-script-guard.mjs").as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        env=_env(tmp_path),
    )
    assert out.returncode == 0, out.stderr[-800:]
    assert json.loads(out.stdout) == [True, False, False, False, False, False, 3]


@pytest.mark.parametrize("rel", TLS_FILES)
def test_scripts_do_not_disable_tls_verification(rel: str) -> None:
    text = (REPO / rel).read_text(encoding="utf-8")
    assert "NODE_TLS_REJECT_UNAUTHORIZED" not in text


def test_no_tls_off_advice_in_tracked_files() -> None:
    """AS-125: no tracked file (docs, comments, scripts) names NODE_TLS_REJECT_UNAUTHORIZED,
    except the guard tests above."""
    git = shutil.which("git")
    if not git or not (REPO / ".git").exists():
        pytest.skip("not a git checkout")
    files = subprocess.run(
        [git, "ls-files", "-z"], cwd=REPO, capture_output=True, check=True
    ).stdout.split(b"\0")
    hits = []
    for raw in files:
        rel = raw.decode()
        path = REPO / rel
        if not rel or rel in TLS_NAME_ALLOWED or not path.is_file():
            continue
        if b"NODE_TLS_REJECT_UNAUTHORIZED" in path.read_bytes():
            hits.append(rel)
    assert hits == []
