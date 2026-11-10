"""AS-113: the request bounds that the pre-AS-90 schemas (3b7d2774) enforced must
be enforced again at the AS-112 entry points: an out-of-bounds value is rejected
(422 over HTTP, pydantic ValidationError at MCP tool / LLM-output validation),
and the boundary value itself is still accepted.

Same harness as tests/test_as112_required_422.py (copied so this file runs alone
on the reference tree): FastAPI TestClient with the service dependency overridden
to an in-process fake running the real read code, the real MCP handlers on a
capturing FastMCP stand-in validated as FastMCP does, and the GraphRAG extractor
with a fake LLM. No network, no DB, no keys. Each case records what it observed
to $AS113_OBS (JSON lines) so ref / tip / after runs can be compared.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import types
import uuid
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

LEARNER = "learner-as113"
HEADERS = {"X-Learner-Id": LEARNER, "X-Role": "learner"}


def _record(test: str, field: str, entry: str, observed: str) -> None:
    out = os.environ.get("AS113_OBS")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps({"test": test, "field": field, "entry": entry, "observed": observed})
                + "\n"
            )


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("CLERK_JWKS_URL", "")
    monkeypatch.setenv("CLERK_ISSUER", "")
    from app.core.settings import get_settings

    get_settings.cache_clear()
    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    yield app, TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _http(resp) -> str:
    return str(resp.status_code)


class _Result:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class _FakeDiagSession:
    def __init__(self, session_row, item_row):
        self.session_row = session_row
        self.item_row = item_row

    async def execute(self, stmt):
        ent = stmt.column_descriptions[0]["entity"].__name__
        return _Result(self.session_row if "Session" in ent else self.item_row)

    async def merge(self, row):
        return row

    async def commit(self):
        return None


def _diag_service(sid: str, iid: str):
    from diagnostic_service.postgres_service import PostgresDiagnosticService
    from diagnostic_service.settings import DiagnosticSettings
    from diagnostic_service.stores.repository import DiagnosticRepository

    session_row = SimpleNamespace(
        id=uuid.UUID(sid), learner_id=LEARNER, status="active", topics=["fractions"], results={}
    )
    item_row = SimpleNamespace(
        id=uuid.UUID(iid),
        topic="fractions",
        subject="math",
        difficulty=0.5,
        stem="1/2+1/2?",
        options={"choices": ["1", "2"], "correct": "A"},
    )
    svc = PostgresDiagnosticService.__new__(PostgresDiagnosticService)
    svc.settings = DiagnosticSettings()
    svc.repo = DiagnosticRepository(svc.settings, session=_FakeDiagSession(session_row, item_row))

    async def _pick_question(**_kw):
        return item_row

    svc.repo.pick_question = _pick_question
    return svc


class _FakeLP:
    async def start_quiz(self, learner_id, plan_id, week_number):
        from schemas.learning_path import QuizStartResponse

        # model_construct: the fake must not depend on which tree's schema is loaded
        return QuizStartResponse.model_construct(quiz_id=str(uuid.uuid4()))

    async def submit_quiz(self, learner_id, quiz_id, answers):
        from learning_path_service.stores.quiz_repository import _score_answers
        from schemas.learning_path import QuizSubmitResponse, StoredQuizItem

        items = [StoredQuizItem.model_construct(id="q1", topic="fractions", correct="A")]
        overall, per_topic, weak = _score_answers(
            items, answers
        )  # the real reads of item_id/chosen
        return QuizSubmitResponse(
            quiz_id=quiz_id, score=overall, per_topic=per_topic, weak_concepts=weak
        )


class _FakeMemory:
    def __init__(self) -> None:
        from memory_service.settings import MemorySettings

        self.settings = MemorySettings()

    async def search(self, input):
        from memory_service.retrieval.policy import allowed_types

        allowed_types(input.agent_id)  # the real read of agent_id (default_service.py:68)
        return []


@pytest.fixture
def mcp_tools(monkeypatch: pytest.MonkeyPatch):
    """Register the real MCP tool handlers on a capturing FastMCP stand-in.

    The mcp package is not installed in this env; FastMCP validates a tool call by
    building a pydantic model from the handler signature, which pydantic.validate_call
    reproduces. A ValidationError there is FastMCP's argument-validation error.
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
        if mod.startswith(("graphrag_mcp", "memory_mcp")):
            monkeypatch.delitem(sys.modules, mod)

    from mcp.server.fastmcp import FastMCP

    def build(kind: str, svc):
        m = FastMCP("as113")
        if kind == "graphrag":
            from graphrag_mcp.tools.kg import register_graphrag_tools

            register_graphrag_tools(m, svc=svc)
        else:
            from memory_mcp.tools.memory import register_memory_tools

            register_memory_tools(m, svc=svc)
        tools = getattr(m, "tools", None)
        if tools is None:  # real FastMCP
            tools = {t.name: t.fn for t in m._tool_manager.list_tools()}
        return tools

    return build


def _call_tool(fn, payload: dict) -> str:
    from pydantic import ValidationError, validate_call

    try:
        asyncio.run(validate_call(fn)(inp=payload))
    except ValidationError:
        return "ValidationError"
    except Exception as exc:  # ToolError from graphrag_mcp/memory_mcp invoke()
        return f"{type(exc).__name__}: {str(exc)[:80]}"
    return "ok"


class _FakeLLM:
    def __init__(self, payload: dict) -> None:
        self.text = json.dumps(payload)

    async def complete(self, _req):
        return SimpleNamespace(text=self.text)


def _extract(payload: dict):
    """Run the GraphRAG extractor's LLM path on a fake LLM response.

    Trees whose Extractor takes no injectable LLM (the original-schema 3b7d2774)
    validate the same LLM JSON with Extraction.model_validate at extractor.py:119;
    that call is what this falls back to there.
    """
    import inspect

    from graphrag_service.ingest.extractor import Extractor
    from graphrag_service.settings import GraphRAGSettings

    if "llm" in inspect.signature(Extractor.__init__).parameters:
        return asyncio.run(Extractor(GraphRAGSettings(), llm=_FakeLLM(payload)).extract(["chunk"]))
    from schemas.graph import Extraction

    return Extraction.model_validate(payload)


# --------------------------------------------------------------------------- cases

REJECT = {"http": "422", "mcp": "ValidationError", "llm": "ValidationError"}
ACCEPT = {"http": "200", "mcp": "ok", "llm": "accepted"}

S8, S9 = "ABCDEFGH", "ABCDEFGHI"
ID128, ID129 = "i" * 128, "i" * 129
Q2000, Q2001 = "q" * 2000, "q" * 2001
WALK = {"seed_node_ids": ["concept:x"]}
COMPACT = {"messages": [{"role": "user", "content": "hi"}], "target_tokens": 1024}
MEM = {"learner_id": LEARNER, "query": "fractions", "agent_id": "tutor"}
ENT = [
    {"name": "Fractions", "kind": "Concept", "confidence": 0.9},
    {"name": "Division", "kind": "Concept", "confidence": 0.8},
]
REL = [
    {"src_name": "Division", "dst_name": "Fractions", "kind": "PREREQUISITE_OF", "confidence": 0.6}
]
LLM = {"entities": ENT, "relations": REL, "claims": [], "confidence": 0.8}


def _ent(conf):
    return {**LLM, "entities": [{**ENT[0], "confidence": conf}, ENT[1]]}


def _rel(conf):
    return {**LLM, "relations": [{**REL[0], "confidence": conf}]}


def _without(d, key):
    return {k: v for k, v in d.items() if k != key}


# (case id, constraint, side, entry kind, entry, payload); side "control" = accept.
CASES = [
    # DiagnosticAnswerRequest.chosen: str = Field(min_length=1, max_length=8)
    (
        "b01a",
        "DiagnosticAnswerRequest.chosen min_length=1",
        "below",
        "http",
        "diag",
        {"chosen": ""},
    ),
    (
        "b01b",
        "DiagnosticAnswerRequest.chosen max_length=8",
        "above",
        "http",
        "diag",
        {"chosen": S9},
    ),
    ("b01c", "DiagnosticAnswerRequest.chosen 1..8", "control", "http", "diag", {"chosen": "A"}),
    ("b01d", "DiagnosticAnswerRequest.chosen 1..8", "control", "http", "diag", {"chosen": S8}),
    # QuizAnswerItem.chosen: str = Field(min_length=1, max_length=8)
    (
        "b02a",
        "QuizAnswerItem.chosen min_length=1",
        "below",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": ""}],
    ),
    (
        "b02b",
        "QuizAnswerItem.chosen max_length=8",
        "above",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": S9}],
    ),
    (
        "b02c",
        "QuizAnswerItem.chosen 1..8",
        "control",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": "A"}],
    ),
    (
        "b02d",
        "QuizAnswerItem.chosen 1..8",
        "control",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": S8}],
    ),
    # QuizAnswerItem.time_spent_s: int | None = Field(default=None, ge=0, le=3600)
    (
        "b03a",
        "QuizAnswerItem.time_spent_s ge=0",
        "below",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": "A", "time_spent_s": -1}],
    ),
    (
        "b03b",
        "QuizAnswerItem.time_spent_s le=3600",
        "above",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": "A", "time_spent_s": 3601}],
    ),
    (
        "b03c",
        "QuizAnswerItem.time_spent_s 0..3600",
        "control",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": "A", "time_spent_s": 0}],
    ),
    (
        "b03d",
        "QuizAnswerItem.time_spent_s 0..3600",
        "control",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": "A", "time_spent_s": 3600}],
    ),
    # QuizSubmitRequest.answers: list[QuizAnswerItem] = Field(min_length=1)
    ("b04a", "QuizSubmitRequest.answers min_length=1", "below", "http", "quiz", []),
    (
        "b04c",
        "QuizSubmitRequest.answers min_length=1",
        "control",
        "http",
        "quiz",
        [{"item_id": "q1", "chosen": "A"}],
    ),
    # KGSearchInput.k: int = Field(default=10, ge=1, le=200)
    ("b05a", "KGSearchInput.k ge=1", "below", "http", "kgsearch", {"query": "fractions", "k": 0}),
    (
        "b05b",
        "KGSearchInput.k le=200",
        "above",
        "http",
        "kgsearch",
        {"query": "fractions", "k": 201},
    ),
    (
        "b05c",
        "KGSearchInput.k 1..200",
        "control",
        "http",
        "kgsearch",
        {"query": "fractions", "k": 1},
    ),
    (
        "b05d",
        "KGSearchInput.k 1..200",
        "control",
        "http",
        "kgsearch",
        {"query": "fractions", "k": 200},
    ),
    (
        "b05e",
        "KGSearchInput.k ge=1 (MCP kg.search)",
        "below",
        "mcp",
        "kg.search",
        {"query": "fractions", "k": 0},
    ),
    # KGWalkInput.depth: int = Field(default=2, ge=1, le=4)
    ("b06a", "KGWalkInput.depth ge=1", "below", "mcp", "kg.walk", {**WALK, "depth": 0}),
    ("b06b", "KGWalkInput.depth le=4", "above", "mcp", "kg.walk", {**WALK, "depth": 5}),
    ("b06c", "KGWalkInput.depth 1..4", "control", "mcp", "kg.walk", {**WALK, "depth": 1}),
    ("b06d", "KGWalkInput.depth 1..4", "control", "mcp", "kg.walk", {**WALK, "depth": 4}),
    # KGWalkInput.limit: int = Field(default=50, ge=1, le=500)
    ("b07a", "KGWalkInput.limit ge=1", "below", "mcp", "kg.walk", {**WALK, "limit": 0}),
    ("b07b", "KGWalkInput.limit le=500", "above", "mcp", "kg.walk", {**WALK, "limit": 501}),
    ("b07c", "KGWalkInput.limit 1..500", "control", "mcp", "kg.walk", {**WALK, "limit": 1}),
    ("b07d", "KGWalkInput.limit 1..500", "control", "mcp", "kg.walk", {**WALK, "limit": 500}),
    # KGWalkInput.seed_node_ids: list[IDStr]  (IDStr = str, min_length=1, max_length=128)
    (
        "b08a",
        "KGWalkInput.seed_node_ids[] IDStr min_length=1",
        "below",
        "mcp",
        "kg.walk",
        {"seed_node_ids": [""]},
    ),
    (
        "b08b",
        "KGWalkInput.seed_node_ids[] IDStr max_length=128",
        "above",
        "mcp",
        "kg.walk",
        {"seed_node_ids": [ID129]},
    ),
    (
        "b08c",
        "KGWalkInput.seed_node_ids[] IDStr 1..128",
        "control",
        "mcp",
        "kg.walk",
        {"seed_node_ids": ["c"]},
    ),
    (
        "b08d",
        "KGWalkInput.seed_node_ids[] IDStr 1..128",
        "control",
        "mcp",
        "kg.walk",
        {"seed_node_ids": [ID128]},
    ),
    # KGHybridInput.learner_id: IDStr | None = None
    (
        "b09a",
        "KGHybridInput.learner_id IDStr min_length=1",
        "below",
        "http",
        "kghybrid",
        {"query": "f", "learner_id": ""},
    ),
    (
        "b09b",
        "KGHybridInput.learner_id IDStr max_length=128",
        "above",
        "http",
        "kghybrid",
        {"query": "f", "learner_id": ID129},
    ),
    (
        "b09c",
        "KGHybridInput.learner_id IDStr 1..128",
        "control",
        "http",
        "kghybrid",
        {"query": "f", "learner_id": "l"},
    ),
    (
        "b09d",
        "KGHybridInput.learner_id IDStr 1..128",
        "control",
        "http",
        "kghybrid",
        {"query": "f", "learner_id": ID128},
    ),
    # CompactionInput.target_tokens: int = Field(ge=512)
    (
        "b10a",
        "CompactionInput.target_tokens ge=512",
        "below",
        "mcp",
        "memory.compact_context",
        {**COMPACT, "target_tokens": 511},
    ),
    (
        "b10c",
        "CompactionInput.target_tokens ge=512",
        "control",
        "mcp",
        "memory.compact_context",
        {**COMPACT, "target_tokens": 512},
    ),
    # CompactionInput.pinned_memory_ids: list[IDStr] = Field(default_factory=list)
    (
        "b11a",
        "CompactionInput.pinned_memory_ids[] IDStr min_length=1",
        "below",
        "mcp",
        "memory.compact_context",
        {**COMPACT, "pinned_memory_ids": [""]},
    ),
    (
        "b11b",
        "CompactionInput.pinned_memory_ids[] IDStr max_length=128",
        "above",
        "mcp",
        "memory.compact_context",
        {**COMPACT, "pinned_memory_ids": [ID129]},
    ),
    (
        "b11c",
        "CompactionInput.pinned_memory_ids[] IDStr 1..128",
        "control",
        "mcp",
        "memory.compact_context",
        {**COMPACT, "pinned_memory_ids": ["m"]},
    ),
    (
        "b11d",
        "CompactionInput.pinned_memory_ids[] IDStr 1..128",
        "control",
        "mcp",
        "memory.compact_context",
        {**COMPACT, "pinned_memory_ids": [ID128]},
    ),
    # MemorySearchInput.query: str = Field(min_length=1, max_length=2000)  (required)
    (
        "b12a",
        "MemorySearchInput.query min_length=1",
        "below",
        "http",
        "memsearch",
        {**MEM, "query": ""},
    ),
    (
        "b12b",
        "MemorySearchInput.query max_length=2000",
        "above",
        "http",
        "memsearch",
        {**MEM, "query": Q2001},
    ),
    (
        "b12e",
        "MemorySearchInput.query required",
        "omitted",
        "http",
        "memsearch",
        _without(MEM, "query"),
    ),
    (
        "b12c",
        "MemorySearchInput.query 1..2000",
        "control",
        "http",
        "memsearch",
        {**MEM, "query": "q"},
    ),
    (
        "b12d",
        "MemorySearchInput.query 1..2000",
        "control",
        "http",
        "memsearch",
        {**MEM, "query": Q2000},
    ),
    (
        "b12f",
        "MemorySearchInput.query max_length=2000 (MCP memory.search)",
        "above",
        "mcp",
        "memory.search",
        {**MEM, "query": Q2001},
    ),
    # MemorySearchInput.k: int = Field(default=10, ge=1, le=200)
    ("b13a", "MemorySearchInput.k ge=1", "below", "http", "memsearch", {**MEM, "k": 0}),
    ("b13b", "MemorySearchInput.k le=200", "above", "http", "memsearch", {**MEM, "k": 201}),
    ("b13c", "MemorySearchInput.k 1..200", "control", "http", "memsearch", {**MEM, "k": 1}),
    ("b13d", "MemorySearchInput.k 1..200", "control", "http", "memsearch", {**MEM, "k": 200}),
    # MemorySearchInput.learner_id: IDStr  (required)
    (
        "b14a",
        "MemorySearchInput.learner_id IDStr min_length=1",
        "below",
        "http",
        "memsearch",
        {**MEM, "learner_id": ""},
    ),
    (
        "b14b",
        "MemorySearchInput.learner_id IDStr max_length=128",
        "above",
        "http",
        "memsearch",
        {**MEM, "learner_id": ID129},
    ),
    (
        "b14e",
        "MemorySearchInput.learner_id required",
        "omitted",
        "http",
        "memsearch",
        _without(MEM, "learner_id"),
    ),
    (
        "b14c",
        "MemorySearchInput.learner_id IDStr 1..128",
        "control",
        "http",
        "memsearch",
        {**MEM, "learner_id": "l"},
    ),
    (
        "b14d",
        "MemorySearchInput.learner_id IDStr 1..128",
        "control",
        "http",
        "memsearch",
        {**MEM, "learner_id": ID128},
    ),
    # MemorySearchInput.min_strength: ConfidenceScore = 0.0  (float, ge=0.0, le=1.0)
    (
        "b15a",
        "MemorySearchInput.min_strength ConfidenceScore ge=0.0",
        "below",
        "http",
        "memsearch",
        {**MEM, "min_strength": -0.1},
    ),
    (
        "b15b",
        "MemorySearchInput.min_strength ConfidenceScore le=1.0",
        "above",
        "http",
        "memsearch",
        {**MEM, "min_strength": 1.1},
    ),
    (
        "b15c",
        "MemorySearchInput.min_strength 0..1",
        "control",
        "http",
        "memsearch",
        {**MEM, "min_strength": 0.0},
    ),
    (
        "b15d",
        "MemorySearchInput.min_strength 0..1",
        "control",
        "http",
        "memsearch",
        {**MEM, "min_strength": 1.0},
    ),
    # Extraction.confidence: ConfidenceScore = 0.5
    (
        "b16a",
        "Extraction.confidence ConfidenceScore ge=0.0",
        "below",
        "llm",
        "extract",
        {**LLM, "confidence": -0.1},
    ),
    (
        "b16b",
        "Extraction.confidence ConfidenceScore le=1.0",
        "above",
        "llm",
        "extract",
        {**LLM, "confidence": 1.1},
    ),
    ("b16c", "Extraction.confidence 0..1", "control", "llm", "extract", {**LLM, "confidence": 0.0}),
    ("b16d", "Extraction.confidence 0..1", "control", "llm", "extract", {**LLM, "confidence": 1.0}),
    # Entity.confidence: ConfidenceScore = 0.5
    ("b17a", "Entity.confidence ConfidenceScore ge=0.0", "below", "llm", "extract", _ent(-0.1)),
    ("b17b", "Entity.confidence ConfidenceScore le=1.0", "above", "llm", "extract", _ent(1.1)),
    ("b17c", "Entity.confidence 0..1", "control", "llm", "extract", _ent(0.0)),
    ("b17d", "Entity.confidence 0..1", "control", "llm", "extract", _ent(1.0)),
    # Relation.confidence: ConfidenceScore = 0.5
    ("b18a", "Relation.confidence ConfidenceScore ge=0.0", "below", "llm", "extract", _rel(-0.1)),
    ("b18b", "Relation.confidence ConfidenceScore le=1.0", "above", "llm", "extract", _rel(1.1)),
    ("b18c", "Relation.confidence 0..1", "control", "llm", "extract", _rel(0.0)),
    ("b18d", "Relation.confidence 0..1", "control", "llm", "extract", _rel(1.0)),
]

ENTRY = {
    "diag": "POST /v1/diagnostic/{id}/answer",
    "quiz": "POST /v1/learners/me/plans/{id}/weeks/{n}/quiz/submit",
    "kgsearch": "POST /v1/graphrag/search",
    "kghybrid": "POST /v1/graphrag/hybrid",
    "memsearch": "POST /v1/memory/search",
    "extract": "Extractor.extract (LLM JSON)",
}


def _run(request, kind: str, entry: str, payload):
    if kind == "http":
        api = request.getfixturevalue("api")
        app, client = api
        if entry == "diag":
            try:
                from diagnostic_service.api import get_diagnostic_service
            except ImportError:
                pytest.skip("no diagnostic service on this tree")
            sid, iid = str(uuid.uuid4()), str(uuid.uuid4())
            app.dependency_overrides[get_diagnostic_service] = lambda: _diag_service(sid, iid)
            resp = client.post(
                f"/v1/diagnostic/{sid}/answer", json={"item_id": iid, **payload}, headers=HEADERS
            )
        elif entry == "quiz":
            try:
                from learning_path_service.api import get_learning_path_service
            except ImportError:
                pytest.skip("no learning_path service on this tree")
            app.dependency_overrides[get_learning_path_service] = lambda: _FakeLP()
            resp = client.post(
                "/v1/learners/me/plans/p1/weeks/1/quiz/submit",
                json={"answers": payload},
                headers=HEADERS,
            )
        elif entry in ("kgsearch", "kghybrid"):
            from graphrag_service.api import get_graphrag_service
            from graphrag_service.default_service import DefaultGraphRAGService

            app.dependency_overrides[get_graphrag_service] = lambda: DefaultGraphRAGService()
            path = "/v1/graphrag/search" if entry == "kgsearch" else "/v1/graphrag/hybrid"
            resp = client.post(path, json=payload, headers=HEADERS)
        else:
            from memory_service.api import get_memory_service

            app.dependency_overrides[get_memory_service] = lambda: _FakeMemory()
            resp = client.post("/v1/memory/search", json=payload, headers=HEADERS)
        if resp.status_code == 404 and "Not Found" in resp.text:
            pytest.skip("route missing on this tree")
        return _http(resp)
    if kind == "mcp":
        build = request.getfixturevalue("mcp_tools")
        if entry.startswith("kg."):
            from graphrag_service.default_service import DefaultGraphRAGService

            return _call_tool(build("graphrag", DefaultGraphRAGService())[entry], payload)
        return _call_tool(build("memory", _FakeMemory())[entry], payload)
    from pydantic import ValidationError

    try:
        _extract(payload)
    except ValidationError:
        return "ValidationError"
    return "accepted"


@pytest.mark.parametrize(
    ("cid", "constraint", "side", "kind", "entry", "payload"), CASES, ids=[c[0] for c in CASES]
)
def test_bound(request, cid, constraint, side, kind, entry, payload) -> None:
    obs = _run(request, kind, entry, payload)
    _record(
        cid,
        constraint,
        f"{side} | MCP {entry}" if kind == "mcp" else f"{side} | {ENTRY[entry]}",
        obs,
    )
    expected = ACCEPT[kind] if side == "control" else REJECT[kind]
    assert obs == expected
