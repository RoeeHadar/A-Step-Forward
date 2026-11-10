"""AS-116: memory read entry points vs agent_id, compared with ref 3b7d2774.

On the ref, MemorySearchInput.agent_id was required. These are the client-facing
reads that took a MemorySearchInput body: POST /v1/memory/search and MCP
memory.search. Omitting agent_id gave 422 / ValidationError there. AS-112
restored that with MemorySearchBody. The other reads (GET /v1/memory with and
without q, GET /v1/memory/timeline) never took agent_id from the client on the
ref: the route supplies "user:memory_inspector" or reads no policy. This file
pins all of them, plus the AS-114 hydrator, on the ref, tip and after (fakes
only). Observations go to $AS116_OBS as JSON lines.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _rel in (
    "packages/schemas",
    "packages/agents",
    "services/memory",
    "services/graphrag",
    "services/orchestrator",
    "services/curriculum",
    "services/learner_model",
    "services/diagnostic",
    "services/learning_path",
    "apps/api",
    "mcp-servers/graphrag/src",
    "mcp-servers/memory/src",
):
    _p = str(_ROOT / _rel)
    if _p not in sys.path:
        sys.path.insert(0, _p)

LEARNER = "learner-as116"
HEADERS = {"X-Learner-Id": LEARNER, "X-Role": "learner"}


def _record(test: str, entry: str, observed: str, agent_id_seen: object = "-") -> None:
    out = os.environ.get("AS116_OBS")
    if out:
        row = {"test": test, "entry": entry, "observed": observed, "agent_id_seen": agent_id_seen}
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")


class _FakeMemory:
    """Runs the real policy read of agent_id, as default_service.py does."""

    def __init__(self) -> None:
        from memory_service.settings import MemorySettings

        self.settings = MemorySettings()
        self.seen: list[object] = []

    async def search(self, input):
        from memory_service.retrieval.policy import allowed_types

        self.seen.append(input.agent_id)
        allowed_types(input.agent_id)
        return []

    async def timeline(self, *, learner_id, k=100, **_k):
        self.seen.append(None)
        return []


# --------------------------------------------------------------------------- HTTP


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("CLERK_JWKS_URL", "")
    monkeypatch.setenv("CLERK_ISSUER", "")
    from app.core.settings import get_settings

    get_settings.cache_clear()
    from app.main import create_app
    from fastapi.testclient import TestClient
    from memory_service.api import get_memory_service

    app = create_app()
    fake = _FakeMemory()
    app.dependency_overrides[get_memory_service] = lambda: fake
    yield fake, TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_r1_post_memory_search_agent_id_omitted_422(api) -> None:
    fake, client = api
    resp = client.post(
        "/v1/memory/search", json={"learner_id": LEARNER, "query": "fractions"}, headers=HEADERS
    )
    _record("r1", "POST /v1/memory/search (agent_id omitted)", str(resp.status_code))
    assert resp.status_code == 422 and fake.seen == []


def test_r1c_post_memory_search_agent_id_set_200(api) -> None:
    fake, client = api
    body = {"learner_id": LEARNER, "query": "fractions", "agent_id": "tutor"}
    resp = client.post("/v1/memory/search", json=body, headers=HEADERS)
    _record("r1c", "POST /v1/memory/search (agent_id='tutor')", str(resp.status_code), fake.seen)
    assert resp.status_code == 200 and fake.seen == ["tutor"]


def test_r3_get_memory_q_server_supplied_agent_id(api) -> None:
    fake, client = api
    resp = client.get("/v1/memory", params={"q": "fractions"}, headers=HEADERS)
    _record("r3", "GET /v1/memory?q= (no client agent_id)", str(resp.status_code), fake.seen)
    assert resp.status_code == 200 and fake.seen == ["user:memory_inspector"]


def test_r4_get_memory_list_no_agent_id(api) -> None:
    fake, client = api
    resp = client.get("/v1/memory", headers=HEADERS)
    _record("r4", "GET /v1/memory (timeline, no agent_id)", str(resp.status_code), fake.seen)
    assert resp.status_code == 200 and fake.seen == [None]


def test_r5_get_memory_timeline_no_agent_id(api) -> None:
    fake, client = api
    resp = client.get("/v1/memory/timeline", headers=HEADERS)
    _record("r5", "GET /v1/memory/timeline (no agent_id)", str(resp.status_code), fake.seen)
    assert resp.status_code == 200 and fake.seen == [None]


# --------------------------------------------------------------------------- MCP


@pytest.fixture
def memory_tools(monkeypatch: pytest.MonkeyPatch):
    """Real memory MCP handlers on a capturing FastMCP stand-in (as in AS-112):
    pydantic.validate_call reproduces FastMCP's argument validation."""
    try:
        import mcp.server.fastmcp  # noqa: F401
    except ImportError:

        class ToolError(Exception):
            pass

        class FastMCP:
            def __init__(self, *a, **k):
                self.tools = {}

            def tool(self, name=None, description=None, **_k):
                def deco(fn):
                    self.tools[name or fn.__name__] = fn
                    return fn

                return deco

        exc_mod = types.ModuleType("mcp.server.fastmcp.exceptions")
        exc_mod.ToolError = ToolError
        fm = types.ModuleType("mcp.server.fastmcp")
        fm.FastMCP = FastMCP
        fm.exceptions = exc_mod
        for name, mod in (
            ("mcp", types.ModuleType("mcp")),
            ("mcp.server", types.ModuleType("mcp.server")),
            ("mcp.server.fastmcp", fm),
            ("mcp.server.fastmcp.exceptions", exc_mod),
        ):
            monkeypatch.setitem(sys.modules, name, mod)
    for mod in list(sys.modules):
        if mod.startswith("memory_mcp"):
            monkeypatch.delitem(sys.modules, mod)

    from mcp.server.fastmcp import FastMCP
    from memory_mcp.tools.memory import register_memory_tools

    fake = _FakeMemory()
    m = FastMCP("as116")
    register_memory_tools(m, svc=fake)
    tools = getattr(m, "tools", None)
    if tools is None:  # real FastMCP
        tools = {t.name: t.fn for t in m._tool_manager.list_tools()}
    return fake, tools


def _call_tool(fn, payload: dict) -> str:
    from pydantic import ValidationError, validate_call

    try:
        asyncio.run(validate_call(fn)(inp=payload))
    except ValidationError:
        return "ValidationError"
    except Exception as exc:  # ToolError from memory_mcp invoke()
        return f"{type(exc).__name__}: {str(exc)[:80]}"
    return "ok"


def test_r2_mcp_memory_search_agent_id_omitted_validation_error(memory_tools) -> None:
    fake, tools = memory_tools
    obs = _call_tool(tools["memory.search"], {"learner_id": LEARNER, "query": "fractions"})
    _record("r2", "MCP memory.search (agent_id omitted)", obs)
    assert obs == "ValidationError" and fake.seen == []


def test_r2c_mcp_memory_search_agent_id_set_ok(memory_tools) -> None:
    fake, tools = memory_tools
    payload = {"learner_id": LEARNER, "query": "fractions", "agent_id": "tutor"}
    obs = _call_tool(tools["memory.search"], payload)
    _record("r2c", "MCP memory.search (agent_id='tutor')", obs, fake.seen)
    assert obs == "ok" and fake.seen == ["tutor"]


# --------------------------------------------------------------------------- hydrator


def test_h1_hydrator_still_returns_no_memories() -> None:
    """AS-114 behaviour unchanged: no agent_id -> no memories, search never reached."""
    from agents.base.memory_hydrator import hydrate

    calls: list[object] = []

    class _Api:
        async def search(self, inp):
            calls.append(inp)
            rec = SimpleNamespace(id="m1", type="semantic", content="likes fractions")
            return [SimpleNamespace(record=rec, score=0.9)]

    out = asyncio.run(hydrate(learner_id=LEARNER, query="fractions", memory_api=_Api()))
    _record(
        "h1", "agents.base.memory_hydrator.hydrate (no agent_id)", f"{len(out.record_ids)} memories"
    )
    assert out.record_ids == [] and out.summary == "" and calls == []
