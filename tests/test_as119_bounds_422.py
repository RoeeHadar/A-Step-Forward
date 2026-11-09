"""AS-119: every remaining request bound from the pre-AS-90 schemas (3b7d2774) is
enforced again at the entry points that take untrusted input.

The AS-119 inventory (items/AS-119/constraints.csv) lists every bound, required
field and IDStr/ConfidenceScore type from the ref that the tip lost at an HTTP
route, an MCP tool signature or the LLM extractor. Each lost constraint is one
case below: an out-of-bounds value (or an omitted required field) must be
rejected (422 over HTTP, pydantic ValidationError at MCP argument validation and
at LLM-output validation), and the service fake must never be called on a
reject. Each (entry point, field) also gets in-bounds boundary controls, which
must reach the service.

The memory MCP tools are also exercised field by field (the 16 AS-90 fallback
sites in memory_mcp/tools/memory.py) with the AS-90 hit store checked to stay
unchanged. A last test checks that the AS-116 no-hits test is collected last.

Same harness as tests/test_as113_bounds_422.py (self-contained so this file runs
on the ref, the tip and after): FastAPI TestClient with service dependencies
overridden by recording fakes, the real MCP handlers on a capturing FastMCP
stand-in validated as FastMCP does, and the GraphRAG extractor on a fake LLM.
No network, no DB, no keys. Observations go to $AS119_OBS as JSON lines.
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import subprocess
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _p in [
    _ROOT / "packages/schemas",
    _ROOT / "packages/agents",
    _ROOT / "apps/api",
    *sorted((_ROOT / "services").glob("*")),
    *sorted((_ROOT / "mcp-servers").glob("*/src")),
]:
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

LEARNER = "learner-as119"
HEADERS = {"X-Learner-Id": LEARNER, "X-Role": "learner"}
MCP_PREFIXES = ("graphrag_mcp", "memory_mcp", "curriculum_mcp", "progress_mcp")


def _record(**row) -> None:
    out = os.environ.get("AS119_OBS")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


class _Recorder:
    """Service / facade / runner fake: any awaited method call is recorded."""

    RETURNS: ClassVar[dict[str, object]] = {"consolidate": 0}

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        async def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return self.RETURNS.get(name)

        return method


class _Runner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    async def stream(self, body, **kwargs):
        self.calls.append(("stream", (body,), kwargs))
        if False:  # pragma: no cover - async generator with no chunks
            yield None


def _fallback_hits(request):
    """The AS-90 hit store (AS-116 fixture); None on trees that have no reporter."""
    try:
        return request.getfixturevalue("as90_fallback_hits")
    except pytest.FixtureLookupError:
        return None


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

    app = create_app()
    yield app, TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


HTTP = {
    # entry key: (method, path, dependency provider "module:attr", fake kind)
    "memwrite": ("POST", "/v1/memory", "memory_service.api:get_memory_service"),
    "memupdate": ("PATCH", "/v1/memory/m1", "memory_service.api:get_memory_service"),
    "chat": ("POST", "/v1/chat", "app.routers.chat:_get_runner"),
    "diagstart": ("POST", "/v1/diagnostic/start", "diagnostic_service.api:get_diagnostic_service"),
    "onboard": (
        "POST",
        "/v1/onboarding/submit",
        "learner_model_service.api:get_learner_model_service",
    ),
}


def _http_call(request, key: str, payload) -> tuple[str, list]:
    import importlib

    app, client = request.getfixturevalue("api")
    method, path, dep = HTTP[key]
    mod, attr = dep.split(":")
    fake = _Runner() if key == "chat" else _Recorder()
    app.dependency_overrides[getattr(importlib.import_module(mod), attr)] = lambda: fake
    resp = client.request(method, path, json=payload, headers=HEADERS)
    if resp.status_code == 404 and "Not Found" in resp.text:
        pytest.skip("route missing on this tree")
    if resp.status_code == 422:
        return "422", fake.calls
    return ("accepted" if fake.calls else f"status {resp.status_code} (not reached)"), fake.calls


# --------------------------------------------------------------------------- MCP


@pytest.fixture
def mcp_tools(monkeypatch: pytest.MonkeyPatch):
    """Register the real MCP tool handlers on a capturing FastMCP stand-in.

    The mcp package is not installed in this env; FastMCP validates a tool call by
    building a pydantic model from the handler signature, which
    pydantic.validate_call reproduces. A ValidationError there is FastMCP's
    argument-validation error.
    """
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
        if mod.startswith(MCP_PREFIXES):
            monkeypatch.delitem(sys.modules, mod)

    from mcp.server.fastmcp import FastMCP

    def build(server: str, fake):
        m = FastMCP("as119")
        if server == "kg":
            from graphrag_mcp.tools.kg import register_graphrag_tools

            register_graphrag_tools(m, svc=fake)
        elif server == "memory":
            from memory_mcp.tools.memory import register_memory_tools

            register_memory_tools(m, svc=fake)
        elif server == "curriculum":
            from curriculum_mcp.tools.curriculum import register_curriculum_tools

            register_curriculum_tools(m, svc=fake)
        else:
            from progress_mcp.tools.progress import register_progress_tools

            register_progress_tools(m, facade=fake)
        tools = getattr(m, "tools", None)
        if tools is None:  # real FastMCP
            tools = {t.name: t.fn for t in m._tool_manager.list_tools()}
        return tools

    return build


def _mcp_call(request, tool: str, payload) -> tuple[str, list]:
    from pydantic import ValidationError, validate_call

    fake = _Recorder()
    fn = request.getfixturevalue("mcp_tools")(tool.split(".")[0], fake)[tool]
    try:
        asyncio.run(validate_call(fn)(inp=payload))
    except ValidationError:
        return "ValidationError", fake.calls
    except Exception as exc:  # ToolError from <server>_mcp invoke()
        return f"{type(exc).__name__}: {str(exc)[:80]}", fake.calls
    return ("ok" if fake.calls else "returned (service not reached)"), fake.calls


# --------------------------------------------------------------------------- LLM


class _FakeLLM:
    def __init__(self, payload: dict) -> None:
        self.text = json.dumps(payload)

    async def complete(self, _req):
        return SimpleNamespace(text=self.text)


def _llm_call(payload: dict) -> tuple[str, list]:
    """Run the GraphRAG extractor's LLM path on a fake LLM response.

    Trees whose Extractor takes no injectable LLM (the ref 3b7d2774) validate the
    same LLM JSON with Extraction.model_validate at extractor.py:119; that call is
    what this falls back to there.
    """
    import inspect

    from graphrag_service.ingest.extractor import Extractor
    from graphrag_service.settings import GraphRAGSettings
    from pydantic import ValidationError

    try:
        if "llm" in inspect.signature(Extractor.__init__).parameters:
            out = asyncio.run(
                Extractor(GraphRAGSettings(), llm=_FakeLLM(payload)).extract(["chunk"])
            )
        else:
            from schemas.graph import Extraction

            out = Extraction.model_validate(payload)
    except ValidationError:
        return "ValidationError", []
    return "accepted", [("extract", (out,), {})]


# --------------------------------------------------------------------------- spec

PROV = {"kind": "chat"}
WRITE = {"learner_id": LEARNER, "type": "semantic", "content": "c", "provenance": PROV}
UPDATE = {"reason": "learner correction"}
ENT = [
    {"name": "Fractions", "kind": "Concept", "confidence": 0.9},
    {"name": "Division", "kind": "Concept", "confidence": 0.8},
]
REL = [
    {"src_name": "Division", "dst_name": "Fractions", "kind": "PREREQUISITE_OF", "confidence": 0.6}
]
CLAIM = {"statement": "Division undoes multiplication.", "supporting_chunk_id": "chunk-1"}

# entry point label -> (kind, target, valid base payload)
ENTRIES = {
    "HTTP POST /v1/memory": ("http", "memwrite", WRITE),
    "HTTP PATCH /v1/memory/{memory_id}": ("http", "memupdate", UPDATE),
    "HTTP POST /v1/chat": ("http", "chat", {"learner_id": LEARNER, "message": "hi"}),
    "HTTP POST /v1/diagnostic/start": ("http", "diagstart", {"topics": ["fractions"]}),
    "HTTP POST /v1/onboarding/submit": (
        "http",
        "onboard",
        {"goal": "pass algebra", "subjects": ["math"], "hours_per_week": 5},
    ),
    "LLM extractor (Extractor.extract JSON)": (
        "llm",
        "extract",
        {"entities": ENT, "relations": REL, "claims": [CLAIM], "confidence": 0.8},
    ),
    "MCP curriculum.list_courses": ("mcp", "curriculum.list_courses", {}),
    "MCP curriculum.get_course": ("mcp", "curriculum.get_course", {"course_id": "course-1"}),
    "MCP curriculum.get_lesson": ("mcp", "curriculum.get_lesson", {"lesson_id": "lesson-1"}),
    "MCP curriculum.find_for_concept": (
        "mcp",
        "curriculum.find_for_concept",
        {"concept_id": "concept-1"},
    ),
    "MCP curriculum.suggest_path": (
        "mcp",
        "curriculum.suggest_path",
        {"learner_id": LEARNER, "goal_id": "goal-1"},
    ),
    "MCP kg.related_concepts": ("mcp", "kg.related_concepts", {"concept_id": "concept-1"}),
    "MCP kg.prereqs": ("mcp", "kg.prereqs", {"concept_id": "concept-1"}),
    "MCP kg.next_topics": (
        "mcp",
        "kg.next_topics",
        {"concept_id": "concept-1", "learner_id": LEARNER},
    ),
    "MCP kg.explain_path": ("mcp", "kg.explain_path", {"src": "concept-1", "dst": "concept-2"}),
    "MCP kg.personalized": (
        "mcp",
        "kg.personalized",
        {"learner_id": LEARNER, "query": "fractions"},
    ),
    "MCP memory.write": ("mcp", "memory.write", {"agent_id": "tutor", "input": WRITE}),
    "MCP memory.timeline": ("mcp", "memory.timeline", {"learner_id": LEARNER}),
    "MCP memory.update": (
        "mcp",
        "memory.update",
        {"memory_id": "m1", "learner_id": LEARNER, "agent_id": "tutor", "patch": UPDATE},
    ),
    "MCP memory.delete": (
        "mcp",
        "memory.delete",
        {"memory_id": "m1", "learner_id": LEARNER, "agent_id": "tutor"},
    ),
    "MCP memory.dream_now": ("mcp", "memory.dream_now", {"learner_id": LEARNER}),
    "MCP memory.consolidate": ("mcp", "memory.consolidate", {"learner_id": LEARNER}),
    "MCP progress.snapshot": ("mcp", "progress.snapshot", {"learner_id": LEARNER}),
    "MCP progress.gaps": ("mcp", "progress.gaps", {"learner_id": LEARNER}),
    "MCP progress.streak": ("mcp", "progress.streak", {"learner_id": LEARNER}),
    "MCP progress.update_mastery": (
        "mcp",
        "progress.update_mastery",
        {"learner_id": LEARNER, "concept_id": "concept-1", "score": 0.5},
    ),
}

ID = (("minLength", 1), ("maxLength", 128), ("required", True))  # required IDStr
OPT_ID = (("minLength", 1), ("maxLength", 128))  # IDStr | None
UNIT = (("minimum", 0.0), ("maximum", 1.0))  # ConfidenceScore

# The lost ref constraints: (entry point, field path, ((constraint, ref value), ...)).
# Field paths use the bounds_diff.py notation: "body." for HTTP bodies, "." for MCP
# tool inputs and the LLM JSON, "[]" for a list element.
LOST = [
    ("HTTP POST /v1/memory", "body.learner_id", ID),
    ("HTTP POST /v1/memory", "body.type", (("required", True),)),
    (
        "HTTP POST /v1/memory",
        "body.content",
        (("minLength", 1), ("maxLength", 20000), ("required", True)),
    ),
    ("HTTP POST /v1/memory", "body.valence", (("minimum", -1.0), ("maximum", 1.0))),
    ("HTTP POST /v1/memory", "body.importance_hint", UNIT),
    ("HTTP POST /v1/memory", "body.provenance", (("required", True),)),
    ("HTTP POST /v1/memory", "body.provenance.kind", (("required", True),)),
    ("HTTP POST /v1/memory", "body.provenance.id", OPT_ID),
    ("HTTP PATCH /v1/memory/{memory_id}", "body.salience", UNIT),
    ("HTTP PATCH /v1/memory/{memory_id}", "body.confidence", UNIT),
    (
        "HTTP PATCH /v1/memory/{memory_id}",
        "body.reason",
        (("minLength", 1), ("maxLength", 500), ("required", True)),
    ),
    ("HTTP POST /v1/chat", "body.learner_id", ID),
    ("HTTP POST /v1/chat", "body.message", (("required", True),)),
    ("HTTP POST /v1/chat", "body.session_id", OPT_ID),
    ("HTTP POST /v1/diagnostic/start", "body.topics", (("maxItems", 20),)),
    (
        "HTTP POST /v1/onboarding/submit",
        "body.goal",
        (("minLength", 1), ("maxLength", 500), ("required", True)),
    ),
    ("HTTP POST /v1/onboarding/submit", "body.subjects", (("minItems", 1), ("required", True))),
    (
        "HTTP POST /v1/onboarding/submit",
        "body.hours_per_week",
        (("minimum", 1.0), ("maximum", 40.0), ("required", True)),
    ),
    ("HTTP POST /v1/onboarding/submit", "body.attention_span", (("minimum", 10), ("maximum", 180))),
    ("LLM extractor (Extractor.extract JSON)", ".claims[].statement", (("required", True),)),
    ("LLM extractor (Extractor.extract JSON)", ".claims[].supporting_chunk_id", ID),
    ("LLM extractor (Extractor.extract JSON)", ".claims[].confidence", UNIT),
    ("MCP curriculum.list_courses", ".limit", (("minimum", 1), ("maximum", 200))),
    ("MCP curriculum.get_course", ".course_id", ID),
    ("MCP curriculum.get_lesson", ".lesson_id", ID),
    ("MCP curriculum.find_for_concept", ".concept_id", ID),
    ("MCP curriculum.find_for_concept", ".limit", (("minimum", 1), ("maximum", 100))),
    ("MCP curriculum.suggest_path", ".learner_id", ID),
    ("MCP curriculum.suggest_path", ".goal_id", ID),
    ("MCP curriculum.suggest_path", ".max_steps", (("minimum", 1), ("maximum", 50))),
    ("MCP kg.related_concepts", ".concept_id", ID),
    ("MCP kg.prereqs", ".concept_id", ID),
    ("MCP kg.next_topics", ".concept_id", ID),
    ("MCP kg.next_topics", ".learner_id", ID),
    ("MCP kg.explain_path", ".src", ID),
    ("MCP kg.explain_path", ".dst", ID),
    ("MCP kg.personalized", ".learner_id", ID),
    ("MCP kg.personalized", ".query", (("minLength", 1), ("maxLength", 2000), ("required", True))),
    ("MCP kg.personalized", ".k", (("minimum", 1), ("maximum", 200))),
    ("MCP memory.write", ".agent_id", (("minLength", 1), ("maxLength", 128), ("required", True))),
    ("MCP memory.write", ".input", (("required", True),)),
    ("MCP memory.write", ".input.learner_id", ID),
    ("MCP memory.write", ".input.type", (("required", True),)),
    (
        "MCP memory.write",
        ".input.content",
        (("minLength", 1), ("maxLength", 20000), ("required", True)),
    ),
    ("MCP memory.write", ".input.valence", (("minimum", -1.0), ("maximum", 1.0))),
    ("MCP memory.write", ".input.importance_hint", UNIT),
    ("MCP memory.write", ".input.provenance", (("required", True),)),
    ("MCP memory.write", ".input.provenance.kind", (("required", True),)),
    ("MCP memory.write", ".input.provenance.id", OPT_ID),
    ("MCP memory.timeline", ".learner_id", ID),
    ("MCP memory.timeline", ".k", (("minimum", 1), ("maximum", 500))),
    ("MCP memory.update", ".memory_id", ID),
    ("MCP memory.update", ".learner_id", ID),
    ("MCP memory.update", ".agent_id", (("minLength", 1), ("maxLength", 128), ("required", True))),
    ("MCP memory.update", ".patch", (("required", True),)),
    ("MCP memory.update", ".patch.salience", UNIT),
    ("MCP memory.update", ".patch.confidence", UNIT),
    (
        "MCP memory.update",
        ".patch.reason",
        (("minLength", 1), ("maxLength", 500), ("required", True)),
    ),
    ("MCP memory.delete", ".memory_id", ID),
    ("MCP memory.delete", ".learner_id", ID),
    ("MCP memory.delete", ".agent_id", (("minLength", 1), ("maxLength", 128), ("required", True))),
    ("MCP memory.dream_now", ".learner_id", ID),
    ("MCP memory.consolidate", ".learner_id", ID),
    ("MCP progress.snapshot", ".learner_id", ID),
    ("MCP progress.gaps", ".learner_id", ID),
    ("MCP progress.streak", ".learner_id", ID),
    ("MCP progress.update_mastery", ".learner_id", ID),
    ("MCP progress.update_mastery", ".concept_id", ID),
    (
        "MCP progress.update_mastery",
        ".score",
        (("minimum", 0.0), ("maximum", 1.0), ("required", True)),
    ),
]


def _keys(path: str) -> list:
    keys: list = []
    for part in path.removeprefix("body").lstrip(".").split("."):
        if part.endswith("[]"):
            keys += [part[:-2], 0]
        else:
            keys.append(part)
    return keys


def _set(payload, path: str, value):
    """Copy of payload with the field at path set to value (or removed if value is _DEL)."""
    out = copy.deepcopy(payload)
    *parents, last = _keys(path)
    node = out
    for k in parents:
        node = node[k]
    if value is _DEL:
        del node[last]
    else:
        node[last] = value
    return out


_DEL = object()


def _value(constraint: str, ref, side: str):
    """The out-of-bounds (side "oob") or boundary (side "edge") value for a bound."""
    if constraint in ("minLength", "maxLength"):
        n = ref - 1 if (constraint == "minLength" and side == "oob") else ref
        n = n + 1 if (constraint == "maxLength" and side == "oob") else n
        return "x" * n
    if constraint in ("minItems", "maxItems"):
        n = ref - 1 if (constraint == "minItems" and side == "oob") else ref
        n = n + 1 if (constraint == "maxItems" and side == "oob") else n
        return [f"topic-{i}" for i in range(n)]
    step = 1 if isinstance(ref, int) else 0.1  # integer fields step by 1 so ints stay ints
    if side == "edge":
        return ref
    return round(ref - step, 6) if constraint == "minimum" else round(ref + step, 6)


def _cases():
    oob, controls = [], []
    for entry, path, cons in LOST:
        base = ENTRIES[entry][2]
        for constraint, ref in cons:
            cid = f"{entry} | {path} | {constraint}"
            if constraint == "required":
                oob.append(
                    pytest.param(entry, path, constraint, ref, _set(base, path, _DEL), id=cid)
                )
                continue
            oob.append(
                pytest.param(
                    entry,
                    path,
                    constraint,
                    ref,
                    _set(base, path, _value(constraint, ref, "oob")),
                    id=cid,
                )
            )
            controls.append(
                pytest.param(
                    entry,
                    path,
                    constraint,
                    ref,
                    _set(base, path, _value(constraint, ref, "edge")),
                    id=cid + " | edge",
                )
            )
        controls.append(
            pytest.param(entry, path, "base", None, base, id=f"{entry} | {path} | base")
        )
    return oob, controls


OOB_CASES, CONTROL_CASES = _cases()
REJECT = {"http": "422", "mcp": "ValidationError", "llm": "ValidationError"}
ACCEPT = {"http": "accepted", "mcp": "ok", "llm": "accepted"}


def _call(request, entry: str, payload) -> tuple[str, str, list]:
    kind, target, _base = ENTRIES[entry]
    if kind == "http":
        return (kind, *_http_call(request, target, payload))
    if kind == "mcp":
        return (kind, *_mcp_call(request, target, payload))
    return (kind, *_llm_call(payload))


@pytest.mark.parametrize(("entry", "path", "constraint", "ref", "payload"), OOB_CASES)
def test_out_of_bounds_rejected(request, entry, path, constraint, ref, payload) -> None:
    kind, observed, calls = _call(request, entry, payload)
    _record(
        test=request.node.callspec.id,
        side="oob",
        entry=entry,
        path=path,
        constraint=constraint,
        ref=ref,
        observed=observed,
        service_called=bool(calls),
    )
    assert observed == REJECT[kind]
    assert calls == [], "service fake was called on a rejected input"


@pytest.mark.parametrize(("entry", "path", "constraint", "ref", "payload"), CONTROL_CASES)
def test_in_bounds_control_accepted(request, entry, path, constraint, ref, payload) -> None:
    kind, observed, calls = _call(request, entry, payload)
    _record(
        test=request.node.callspec.id,
        side="control",
        entry=entry,
        path=path,
        constraint=constraint,
        ref=ref,
        observed=observed,
        service_called=bool(calls),
    )
    assert observed == ACCEPT[kind]


# ------------------------------------------------- curriculum.list_courses level


@pytest.mark.parametrize(
    ("level", "side"), [("expert", "oob"), ("beginner", "control"), ("advanced", "control")]
)
def test_list_courses_level_is_ref_enum(request, level, side) -> None:
    """3b7d2774: level: Level | None (beginner/intermediate/advanced). The repository
    filters on level.value, so an accepted level must carry .value as on the ref."""
    observed, calls = _mcp_call(request, "curriculum.list_courses", {"level": level})
    seen = calls[0][2].get("level") if calls else None
    _record(
        test=f"level:{level}",
        side=side,
        entry="MCP curriculum.list_courses",
        path=".level",
        constraint="enum",
        ref=["beginner", "intermediate", "advanced"],
        observed=observed,
        service_called=bool(calls),
        level_value=getattr(seen, "value", None),
    )
    if side == "oob":
        assert observed == "ValidationError"
        assert calls == []
    else:
        assert observed == "ok"
        assert getattr(seen, "value", None) == level


# ----------------------------------------------- MCP memory writes without agent_id


@pytest.mark.parametrize("tool", ["memory.write", "memory.update", "memory.delete"])
def test_memory_write_tools_reject_missing_agent_id(request, tool) -> None:
    payload = _set(ENTRIES[f"MCP {tool}"][2], ".agent_id", _DEL)
    observed, calls = _mcp_call(request, tool, payload)
    _record(
        test=f"agent_id:{tool}",
        side="oob",
        entry=f"MCP {tool}",
        path=".agent_id",
        constraint="required",
        ref=True,
        observed=observed,
        service_called=bool(calls),
    )
    assert observed == "ValidationError"
    assert calls == [], "memory service (and its audit write) must not be reached"


# ------------------------------------------- the 16 AS-90 fallback sites (memory MCP)

# (site, tool, payload, which service argument carries the field, expected value)
_TL = {
    "learner_id": LEARNER,
    "since": "2026-01-01T00:00:00Z",
    "until": "2026-02-01T00:00:00Z",
    "k": 7,
}
_UP = {"memory_id": "m1", "learner_id": LEARNER, "agent_id": "tutor", "patch": UPDATE}
_DL = {"memory_id": "m1", "learner_id": LEARNER, "agent_id": "tutor", "hard": True}
_WR = {"agent_id": "tutor", "input": WRITE}
SITES = [
    ("MemoryWriteToolInput.agent_id :38", "memory.write", _WR, ("kw", "agent_id"), "tutor"),
    ("MemoryWriteToolInput.input :38", "memory.write", _WR, ("arg", 0, "content"), "c"),
    ("MemoryTimelineInput.learner_id :47", "memory.timeline", _TL, ("kw", "learner_id"), LEARNER),
    ("MemoryTimelineInput.since :47", "memory.timeline", _TL, ("kw", "since"), _TL["since"]),
    ("MemoryTimelineInput.until :47", "memory.timeline", _TL, ("kw", "until"), _TL["until"]),
    ("MemoryTimelineInput.k :47", "memory.timeline", _TL, ("kw", "k"), 7),
    ("MemoryUpdateToolInput.memory_id :53", "memory.update", _UP, ("arg", 0), "m1"),
    (
        "MemoryUpdateToolInput.patch :53",
        "memory.update",
        _UP,
        ("arg", 1, "reason"),
        UPDATE["reason"],
    ),
    ("MemoryUpdateToolInput.learner_id :53", "memory.update", _UP, ("kw", "learner_id"), LEARNER),
    ("MemoryUpdateToolInput.agent_id :53", "memory.update", _UP, ("kw", "agent_id"), "tutor"),
    ("MemoryDeleteToolInput.memory_id :59", "memory.delete", _DL, ("arg", 0), "m1"),
    ("MemoryDeleteToolInput.learner_id :59", "memory.delete", _DL, ("kw", "learner_id"), LEARNER),
    ("MemoryDeleteToolInput.agent_id :59", "memory.delete", _DL, ("kw", "agent_id"), "tutor"),
    ("MemoryDeleteToolInput.hard :59", "memory.delete", _DL, ("kw", "hard"), True),
    (
        "LearnerOnlyInput.learner_id :65",
        "memory.dream_now",
        {"learner_id": LEARNER},
        ("kw", "learner_id"),
        LEARNER,
    ),
    (
        "LearnerOnlyInput.learner_id :69",
        "memory.consolidate",
        {"learner_id": LEARNER},
        ("kw", "learner_id"),
        LEARNER,
    ),
]


@pytest.mark.parametrize(
    ("site", "tool", "payload", "where", "expected"), SITES, ids=[s[0] for s in SITES]
)
def test_memory_tool_site_reads_declared_field(
    request, site, tool, payload, where, expected
) -> None:
    hits = _fallback_hits(request)
    before = dict(hits) if hits is not None else None
    observed, calls = _mcp_call(request, tool, payload)
    new = (
        None
        if hits is None
        else sorted(
            f"{c}.{f} {loc}" for (c, f, loc), n in hits.items() if before.get((c, f, loc)) != n
        )
    )
    field = site.split(" ")[0].split(".", 1)[1]  # e.g. "agent_id"
    site_hits = None if new is None else [h for h in new if h.split(" ")[0].endswith(f".{field}")]
    value = None
    if len(calls) == 1:
        _name, args, kwargs = calls[0]
        value = kwargs.get(where[1]) if where[0] == "kw" else args[where[1]]
        for attr in where[2:]:  # the declared model, or a raw dict via the AS-90 fallback
            value = value.get(attr) if isinstance(value, dict) else getattr(value, attr, None)
    _record(
        test=f"site:{site}",
        side="site",
        entry=f"MCP {tool}",
        path=site,
        constraint="fallback hits",
        ref=None,
        observed=site_hits,
        service_called=bool(calls),
    )
    assert observed == "ok", observed
    assert value == expected
    assert not site_hits, f"AS-90 fallback read at {site}: {site_hits}"
    assert not new, f"AS-90 fallback reads during the {tool} call: {new}"


# ---------------------------------------- AS-116 no-hits check is collected last

_LAST = "test_session_recorded_no_fallback_hits"


def _root_conftest():
    target = (_ROOT / "conftest.py").resolve()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f and Path(f).resolve() == target:
            return mod
    return None


def test_no_hits_hook_moves_check_last() -> None:
    conf = _root_conftest()
    hook = getattr(conf, "pytest_collection_modifyitems", None)
    if hook is None:
        pytest.skip("no AS-116 collection hook on this tree")
    items = [SimpleNamespace(name=n) for n in ("test_a", _LAST, "test_zz_after", "test_zzz")]
    hook(items=items)
    assert [i.name for i in items] == ["test_a", "test_zz_after", "test_zzz", _LAST]


def test_no_hits_check_collected_last_in_inner_session(tmp_path: Path) -> None:
    """An inner pytest session where a file sorts (and is given) after the AS-116
    file: the no-hits check must still be the last collected item."""
    as116 = _ROOT / "tests" / "test_as116_no_fallback_hits.py"
    if not as116.exists():
        pytest.skip("no AS-116 no-hits test on this tree")
    after = tmp_path / "test_zzzz_sorts_after.py"
    after.write_text("def test_zzzz_one():\n    pass\n\n\ndef test_zzzz_two():\n    pass\n")
    before = tmp_path / "test_aaaa_sorts_before.py"
    before.write_text("def test_aaaa():\n    pass\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "AS119_"))}
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            "--rootdir",
            str(_ROOT),
            str(before),
            str(as116),
            str(after),
        ],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    ids = [ln for ln in proc.stdout.splitlines() if "::" in ln]
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert any("test_zzzz_two" in i for i in ids), ids
    assert ids[-1].endswith(f"::{_LAST}"), ids
