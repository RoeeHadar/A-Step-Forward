"""AS-108: GraphRAG model load leaves process-wide TLS state alone; memory has no Voyage default.

A fake ``sentence_transformers`` module stands in for the real library, so nothing is
downloaded and there is no network. Every test snapshots the process-wide TLS state
(ssl default context, TLS-related env vars, httpx and requests defaults) before the
embedder loads the model and asserts it is unchanged afterwards. monkeypatch restores
the originals, so a failing (base) run cannot leak TLS-off into later tests.
"""

from __future__ import annotations

import asyncio
import importlib.util
import os
import ssl
import sys
import types
from pathlib import Path
from typing import ClassVar

import httpx
import pytest
import requests

REPO = Path(__file__).resolve().parents[1]
GRAPHRAG = REPO / "services" / "graphrag" / "graphrag_service"
MEMORY_SETTINGS = REPO / "services" / "memory" / "memory_service" / "settings.py"
TLS_ENV = (
    "HF_HUB_DISABLE_SSL",
    "CURL_CA_BUNDLE",
    "REQUESTS_CA_BUNDLE",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "PYTHONHTTPSVERIFY",
    "NODE_TLS_REJECT_UNAUTHORIZED",
    "HF_HUB_OFFLINE",
    "TRANSFORMERS_OFFLINE",
)


def _load(name: str, path: Path, monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, mod)
    spec.loader.exec_module(mod)
    return mod


def _load_embedder(monkeypatch: pytest.MonkeyPatch) -> tuple[types.ModuleType, types.ModuleType]:
    """Load embedder.py + settings.py by path, skipping the package __init__ chain."""
    pkg = types.ModuleType("graphrag_service")
    pkg.__path__ = [str(GRAPHRAG)]
    sub = types.ModuleType("graphrag_service.ingest")
    sub.__path__ = [str(GRAPHRAG / "ingest")]
    monkeypatch.setitem(sys.modules, "graphrag_service", pkg)
    monkeypatch.setitem(sys.modules, "graphrag_service.ingest", sub)
    settings = _load("graphrag_service.settings", GRAPHRAG / "settings.py", monkeypatch)
    embedder = _load(
        "graphrag_service.ingest.embedder", GRAPHRAG / "ingest" / "embedder.py", monkeypatch
    )
    return embedder, settings


class _Vec(list):
    def tolist(self) -> list[float]:
        return list(self)


class FakeSentenceTransformer:
    calls: ClassVar[list[tuple[tuple, dict]]] = []

    def __init__(self, *args, **kwargs) -> None:
        FakeSentenceTransformer.calls.append((args, kwargs))

    def encode(self, texts, normalize_embeddings=False):
        return [_Vec([float(len(t)), 0.0, 1.0]) for t in texts]


def _tls_state() -> dict[str, object]:
    client = httpx.Client()
    try:
        httpx_verify = client._transport._pool._ssl_context.verify_mode
    finally:
        client.close()
    session = requests.Session()
    return {
        "ssl._create_default_https_context": ssl._create_default_https_context,
        "ssl default verify_mode": ssl._create_default_https_context().verify_mode,
        "env": {k: os.environ.get(k) for k in TLS_ENV},
        "httpx.Client.__init__": httpx.Client.__init__,
        "httpx.AsyncClient.__init__": httpx.AsyncClient.__init__,
        "httpx client verify_mode": httpx_verify,
        "requests.Session.__init__": requests.Session.__init__,
        "requests Session().verify": session.verify,
        "requests.Session.request": requests.Session.request,
    }


@pytest.fixture
def clean_tls(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Pin the current TLS globals so monkeypatch undoes any change the code under test makes."""
    for k in TLS_ENV:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(ssl, "_create_default_https_context", ssl.create_default_context)
    monkeypatch.setattr(httpx.Client, "__init__", httpx.Client.__init__)
    monkeypatch.setattr(httpx.AsyncClient, "__init__", httpx.AsyncClient.__init__)
    monkeypatch.setattr(requests.Session, "__init__", requests.Session.__init__)
    monkeypatch.setattr(requests.Session, "request", requests.Session.request)
    fake = types.ModuleType("sentence_transformers")
    fake.SentenceTransformer = FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake)
    FakeSentenceTransformer.calls = []
    before = _tls_state()
    assert before["ssl default verify_mode"] == ssl.CERT_REQUIRED
    assert before["httpx client verify_mode"] == ssl.CERT_REQUIRED
    assert before["requests Session().verify"] is True
    return before


def test_model_load_leaves_process_tls_state_unchanged(
    monkeypatch: pytest.MonkeyPatch, clean_tls: dict[str, object]
) -> None:
    embedder_mod, settings_mod = _load_embedder(monkeypatch)
    emb = embedder_mod.Embedder(settings_mod.GraphRAGSettings())
    emb._load_st_model()
    assert FakeSentenceTransformer.calls == [(("all-MiniLM-L6-v2",), {})]
    assert _tls_state() == clean_tls


def test_embed_texts_with_fake_model_keeps_tls_and_vectors(
    monkeypatch: pytest.MonkeyPatch, clean_tls: dict[str, object]
) -> None:
    embedder_mod, settings_mod = _load_embedder(monkeypatch)
    emb = embedder_mod.Embedder(settings_mod.GraphRAGSettings())
    vecs = asyncio.run(emb.embed_texts(["ab", "abcd"]))
    assert vecs == [[2.0, 0.0, 1.0], [4.0, 0.0, 1.0]]
    assert _tls_state() == clean_tls


def test_local_files_only_is_scoped_to_the_load(
    monkeypatch: pytest.MonkeyPatch, clean_tls: dict[str, object]
) -> None:
    monkeypatch.setenv("EMBEDDING_LOCAL_FILES_ONLY", "1")
    embedder_mod, settings_mod = _load_embedder(monkeypatch)
    emb = embedder_mod.Embedder(settings_mod.GraphRAGSettings())
    emb._load_st_model()
    assert FakeSentenceTransformer.calls == [(("all-MiniLM-L6-v2",), {"local_files_only": True})]
    # No HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE (or any TLS var) left behind in the process.
    assert _tls_state() == clean_tls


def test_memory_settings_has_no_voyage_embedding_default(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("as108_memory_settings", MEMORY_SETTINGS, monkeypatch)
    assert "embedding_model" not in mod.MemorySettings.model_fields
    assert "voyage" not in MEMORY_SETTINGS.read_text(encoding="utf-8").lower()
    # An EMBEDDING_MODEL env var (shared with graphrag) is still ignored, not an error.
    monkeypatch.setenv("EMBEDDING_MODEL", "voyage-3-large")
    s = mod.MemorySettings()
    assert not hasattr(s, "embedding_model")
    assert s.embedding_dim == 1024
