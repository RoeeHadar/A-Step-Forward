"""AS-97: embedding call sites against ADR-0004 (fakes only, no network, no keys).

- The GraphRAG embedder never posts to Voyage (ADR-0004 hard constraint #1),
  even with a Voyage model and a (placeholder) VOYAGE_API_KEY.
- .env.example no longer defaults EMBEDDING_MODEL to Voyage.
- Script-only NVIDIA embedding calls (rag-ingest / rag-eval / lib/rag-embed.mjs)
  sit behind the AS-96 opt-in (ALLOW_REAL_LLM=1), and the manual RAG Ingest
  workflow sets that opt-in so its behaviour is unchanged.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
GRAPHRAG = REPO / "services" / "graphrag" / "graphrag_service"
PLACEHOLDER_KEY = "placeholder-not-a-real-key"


def _load_embedder(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[types.ModuleType, types.ModuleType]:
    """Load embedder.py + settings.py by path, skipping the package __init__ chain."""
    pkg = types.ModuleType("graphrag_service")
    pkg.__path__ = [str(GRAPHRAG)]
    sub = types.ModuleType("graphrag_service.ingest")
    sub.__path__ = [str(GRAPHRAG / "ingest")]
    monkeypatch.setitem(sys.modules, "graphrag_service", pkg)
    monkeypatch.setitem(sys.modules, "graphrag_service.ingest", sub)
    mods = {}
    for name, path in (
        ("graphrag_service.settings", GRAPHRAG / "settings.py"),
        ("graphrag_service.ingest.embedder", GRAPHRAG / "ingest" / "embedder.py"),
    ):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, mod)
        spec.loader.exec_module(mod)
        mods[name] = mod
    return mods["graphrag_service.ingest.embedder"], mods["graphrag_service.settings"]


def test_graphrag_embedder_never_posts_to_voyage(monkeypatch: pytest.MonkeyPatch) -> None:
    import httpx

    posts: list[str] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"data": [{"embedding": [0.0] * 384}, {"embedding": [0.0] * 384}]}

    class FakeAsyncClient:
        def __init__(self, *a, **k) -> None:
            pass

        async def __aenter__(self) -> FakeAsyncClient:
            return self

        async def __aexit__(self, *exc) -> None:
            return None

        async def post(self, url, **kwargs) -> FakeResponse:
            posts.append(str(url))
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    monkeypatch.setenv("VOYAGE_API_KEY", PLACEHOLDER_KEY)
    monkeypatch.chdir(REPO / "tests")  # no .env file is read from here
    embedder_mod, settings_mod = _load_embedder(monkeypatch)
    settings = settings_mod.GraphRAGSettings(embedding_model="voyage-3-large")
    emb = embedder_mod.Embedder(settings)
    vecs = asyncio.run(emb.embed_texts(["limits", "derivatives"]))
    assert posts == [], f"Voyage was called: {posts}"
    assert len(vecs) == 2 and all(len(v) == settings.embedding_dim for v in vecs)
    assert vecs[0] == emb._deterministic("limits")


def test_env_example_has_no_voyage_default() -> None:
    lines = (REPO / ".env.example").read_text(encoding="utf-8").splitlines()
    kv = dict(ln.split("=", 1) for ln in lines if "=" in ln and not ln.lstrip().startswith("#"))
    assert kv.get("EMBEDDING_MODEL", "").startswith("sentence-transformers/"), kv.get(
        "EMBEDDING_MODEL"
    )
    assert "VOYAGE_API_KEY" not in kv


def test_rag_ingest_workflow_sets_explicit_opt_in() -> None:
    wf = yaml.safe_load((REPO / ".github/workflows/rag-ingest.yml").read_text(encoding="utf-8"))
    assert str(wf["jobs"]["ingest"]["env"].get("ALLOW_REAL_LLM")) == "1"


def _no_net_prefix() -> list[str]:
    unshare = shutil.which("unshare")
    assert unshare, "unshare is required so an unguarded script cannot reach the network"
    assert subprocess.run([unshare, "-rn", "true"], capture_output=True).returncode == 0
    return [unshare, "-rn"]


def _env(tmp_path: Path, **extra: str) -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "NVIDIA_API_KEY": PLACEHOLDER_KEY,
        "DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:9/none",
    }
    env.update(extra)  # ALLOW_REAL_LLM/EVAL_REAL are only present if a test passes them
    return env


def _sandbox(tmp_path: Path, rel: str) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(REPO / "scripts" / "lib", root / "scripts" / "lib")
    (root / "node_modules").symlink_to(REPO / "node_modules")
    dst = root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / rel, dst)
    return root


@pytest.mark.parametrize("rel", ["scripts/rag-ingest.mjs", "scripts/rag-eval.mjs"])
def test_rag_scripts_refuse_without_opt_in(tmp_path: Path, rel: str) -> None:
    root = _sandbox(tmp_path, rel)
    out = subprocess.run(
        [*_no_net_prefix(), "node", str(root / rel)],
        cwd=root,
        env=_env(tmp_path),
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert out.returncode == 3, (out.returncode, out.stdout[-600:], out.stderr[-600:])
    assert "[llm-guard]" in out.stderr and "ALLOW_REAL_LLM=1" in out.stderr
    assert PLACEHOLDER_KEY not in out.stdout + out.stderr


_RAG_EMBED_PROBE = r"""
const calls = [];
globalThis.fetch = async (url) => {
  calls.push(String(url));
  const body = { data: [{ index: 0, embedding: new Array(1024).fill(0) }] };
  return { ok: true, status: 200, json: async () => body, text: async () => '' };
};
const m = await import(process.argv[1]);
let vecs = null, error = null;
try {
  const e = m.makeEmbedder({ apiKey: process.env.NVIDIA_API_KEY });
  vecs = await e.embedBatch(['x'], 'query');
} catch (err) { error = { name: err.name, message: err.message }; }
console.log(JSON.stringify({ calls, n: vecs ? vecs.length : null, error }));
"""


def _probe_rag_embed(tmp_path: Path, **extra: str) -> dict:
    root = _sandbox(tmp_path, "scripts/lib/rag-embed.mjs")
    lib = (root / "scripts" / "lib" / "rag-embed.mjs").as_uri()
    out = subprocess.run(
        [*_no_net_prefix(), "node", "--input-type=module", "-e", _RAG_EMBED_PROBE, lib],
        cwd=root,
        env=_env(tmp_path, **extra),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr[-600:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_rag_embed_lib_refuses_without_opt_in_and_fetches_with_it(tmp_path: Path) -> None:
    refused = _probe_rag_embed(tmp_path / "a")
    assert refused["calls"] == [], refused
    assert refused["error"] and refused["error"]["name"] == "LlmScriptGuardError", refused

    allowed = _probe_rag_embed(tmp_path / "b", ALLOW_REAL_LLM="1")
    assert allowed["error"] is None and allowed["n"] == 1 and len(allowed["calls"]) == 1, allowed
