"""AS-112: request fields that were required before AS-90 must be rejected again
(422 over HTTP, pydantic ValidationError at MCP tool / service-input validation)
when omitted, instead of crashing inside the service (500 / internal_error).

Fakes only: FastAPI TestClient with the service dependency overridden to an
in-process fake that runs the real read code, MCP handlers validated exactly as
FastMCP does (pydantic validation of the handler signature), and the GraphRAG
extractor with a fake LLM. No network, no DB, no keys.

Each omission test asserts the pre-AS-90 reference behaviour and records what it
observed to $AS112_OBS (JSON lines) so the same file can be run on the
reference tree, the tip before the fix and the tip after the fix.
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

LEARNER = "learner-as112"
HEADERS = {"X-Learner-Id": LEARNER, "X-Role": "learner"}


def _record(test: str, field: str, entry: str, observed: str) -> None:
    out = os.environ.get("AS112_OBS")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps({"test": test, "field": field, "entry": entry, "observed": observed})
                + "\n"
            )


# --------------------------------------------------------------------------- HTTP


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


# -- diagnostic: real PostgresDiagnosticService.answer + real DiagnosticRepository
#    reads, with a fake AsyncSession.


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


def _diag_post(api, body: dict) -> str:
    app, client = api
    try:
        from diagnostic_service.api import get_diagnostic_service
    except ImportError:
        pytest.skip("no diagnostic service on this tree")
    sid, iid = str(uuid.uuid4()), str(uuid.uuid4())
    body = {k: (iid if v == "<iid>" else v) for k, v in body.items()}
    app.dependency_overrides[get_diagnostic_service] = lambda: _diag_service(sid, iid)
    resp = api[1].post(f"/v1/diagnostic/{sid}/answer", json=body, headers=HEADERS)
    if resp.status_code == 404 and "Not Found" in resp.text:
        pytest.skip("no diagnostic answer route on this tree")
    return _http(resp)


def test_f01_diagnostic_answer_item_id_omitted(api) -> None:
    obs = _diag_post(api, {"chosen": "A"})
    _record("f01", "DiagnosticAnswerRequest.item_id", "POST /v1/diagnostic/{id}/answer", obs)
    assert obs == "422"


def test_f02_diagnostic_answer_chosen_omitted(api) -> None:
    obs = _diag_post(api, {"item_id": "<iid>"})
    _record("f02", "DiagnosticAnswerRequest.chosen", "POST /v1/diagnostic/{id}/answer", obs)
    assert obs == "422"


def test_c01_diagnostic_answer_control(api) -> None:
    obs = _diag_post(api, {"item_id": "<iid>", "chosen": "A"})
    _record(
        "c01", "DiagnosticAnswerRequest (control, all set)", "POST /v1/diagnostic/{id}/answer", obs
    )
    assert obs == "200"


# -- graphrag routes: real in-memory DefaultGraphRAGService.


def _graph_post(api, path: str, body: dict) -> str:
    app, client = api
    from graphrag_service.api import get_graphrag_service
    from graphrag_service.default_service import DefaultGraphRAGService

    app.dependency_overrides[get_graphrag_service] = lambda: DefaultGraphRAGService()
    return _http(client.post(path, json=body, headers=HEADERS))


def test_f03_kg_search_query_omitted(api) -> None:
    obs = _graph_post(api, "/v1/graphrag/search", {"k": 5})
    _record("f03", "KGSearchInput.query", "POST /v1/graphrag/search", obs)
    assert obs == "422"


def test_f04_kg_hybrid_query_omitted(api) -> None:
    obs = _graph_post(api, "/v1/graphrag/hybrid", {"k": 5})
    _record("f04", "KGHybridInput.query", "POST /v1/graphrag/hybrid", obs)
    assert obs == "422"


# -- quiz submit: fake learning-path service running the real _score_answers reads.


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


def _quiz_post(api, answers: list[dict]) -> str:
    app, client = api
    try:
        from learning_path_service.api import get_learning_path_service
    except ImportError:
        pytest.skip("no learning_path service on this tree")
    app.dependency_overrides[get_learning_path_service] = lambda: _FakeLP()
    resp = client.post(
        "/v1/learners/me/plans/p1/weeks/1/quiz/submit", json={"answers": answers}, headers=HEADERS
    )
    if resp.status_code == 404 and "Not Found" in resp.text:
        pytest.skip("no quiz submit route on this tree")
    return _http(resp)


def test_f06_quiz_answer_item_id_omitted(api) -> None:
    obs = _quiz_post(api, [{"chosen": "A"}])
    _record(
        "f06",
        "QuizAnswerItem.item_id",
        "POST /v1/learners/me/plans/{id}/weeks/{n}/quiz/submit",
        obs,
    )
    assert obs == "422"


def test_f07_quiz_answer_chosen_omitted(api) -> None:
    obs = _quiz_post(api, [{"item_id": "q1"}])
    _record(
        "f07", "QuizAnswerItem.chosen", "POST /v1/learners/me/plans/{id}/weeks/{n}/quiz/submit", obs
    )
    assert obs == "422"


def test_c07_quiz_submit_control_all_fields(api) -> None:
    """Control: the same request with both fields set is accepted (proves the fake works)."""
    obs = _quiz_post(api, [{"item_id": "q1", "chosen": "a"}])
    _record("c07", "QuizAnswerItem (control, all set)", "POST .../quiz/submit", obs)
    assert obs == "200"


# -- memory search route: fake service running the real policy read of agent_id.


class _FakeMemory:
    def __init__(self) -> None:
        from memory_service.settings import MemorySettings

        self.settings = MemorySettings()

    async def search(self, input):
        from memory_service.retrieval.policy import allowed_types

        allowed_types(input.agent_id)  # the real read of agent_id (default_service.py:68)
        return []


def test_f12_memory_search_agent_id_omitted(api) -> None:
    app, client = api
    from memory_service.api import get_memory_service

    app.dependency_overrides[get_memory_service] = lambda: _FakeMemory()
    obs = _http(
        client.post(
            "/v1/memory/search", json={"learner_id": LEARNER, "query": "fractions"}, headers=HEADERS
        )
    )
    _record("f12", "MemorySearchInput.agent_id", "POST /v1/memory/search", obs)
    assert obs == "422"


def test_c12_memory_search_control(api) -> None:
    app, client = api
    from memory_service.api import get_memory_service

    app.dependency_overrides[get_memory_service] = lambda: _FakeMemory()
    body = {"learner_id": LEARNER, "query": "fractions", "agent_id": "tutor"}
    obs = _http(client.post("/v1/memory/search", json=body, headers=HEADERS))
    _record("c12", "MemorySearchInput (control, all set)", "POST /v1/memory/search", obs)
    assert obs == "200"


def test_c03_kg_search_control(api) -> None:
    obs = _graph_post(api, "/v1/graphrag/search", {"query": "fractions", "k": 5})
    _record("c03", "KGSearchInput (control, all set)", "POST /v1/graphrag/search", obs)
    assert obs == "200"


# --------------------------------------------------------------------------- MCP


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
        m = FastMCP("as112")
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


def test_f05_mcp_kg_walk_seed_node_ids_omitted(mcp_tools) -> None:
    from graphrag_service.default_service import DefaultGraphRAGService

    obs = _call_tool(mcp_tools("graphrag", DefaultGraphRAGService())["kg.walk"], {"depth": 1})
    _record("f05", "KGWalkInput.seed_node_ids", "MCP kg.walk", obs)
    assert obs == "ValidationError"


def test_f03b_mcp_kg_search_query_omitted(mcp_tools) -> None:
    from graphrag_service.default_service import DefaultGraphRAGService

    obs = _call_tool(mcp_tools("graphrag", DefaultGraphRAGService())["kg.search"], {"k": 3})
    _record("f03b", "KGSearchInput.query", "MCP kg.search", obs)
    assert obs == "ValidationError"


def test_f04b_mcp_kg_hybrid_query_omitted(mcp_tools) -> None:
    from graphrag_service.default_service import DefaultGraphRAGService

    obs = _call_tool(mcp_tools("graphrag", DefaultGraphRAGService())["kg.hybrid"], {"k": 3})
    _record("f04b", "KGHybridInput.query", "MCP kg.hybrid", obs)
    assert obs == "ValidationError"


def test_c05_mcp_kg_walk_control(mcp_tools) -> None:
    from graphrag_service.default_service import DefaultGraphRAGService

    obs = _call_tool(
        mcp_tools("graphrag", DefaultGraphRAGService())["kg.walk"], {"seed_node_ids": ["concept:x"]}
    )
    _record("c05", "KGWalkInput (control, all set)", "MCP kg.walk", obs)
    assert obs == "ok"


def test_f08_mcp_compact_context_messages_omitted(mcp_tools) -> None:
    obs = _call_tool(
        mcp_tools("memory", _FakeMemory())["memory.compact_context"], {"target_tokens": 1024}
    )
    _record("f08", "CompactionInput.messages", "MCP memory.compact_context", obs)
    assert obs == "ValidationError"


def test_f09_mcp_compact_context_target_tokens_omitted(mcp_tools) -> None:
    payload = {"messages": [{"role": "user", "content": "hi"}]}
    obs = _call_tool(mcp_tools("memory", _FakeMemory())["memory.compact_context"], payload)
    _record("f09", "CompactionInput.target_tokens", "MCP memory.compact_context", obs)
    assert obs == "ValidationError"


def test_c08_mcp_compact_context_control(mcp_tools) -> None:
    payload = {"messages": [{"role": "user", "content": "hi"}], "target_tokens": 1024}
    obs = _call_tool(mcp_tools("memory", _FakeMemory())["memory.compact_context"], payload)
    _record("c08", "CompactionInput (control, all set)", "MCP memory.compact_context", obs)
    assert obs == "ok"


def test_f12b_mcp_memory_search_agent_id_omitted(mcp_tools) -> None:
    payload = {"learner_id": LEARNER, "query": "fractions"}
    obs = _call_tool(mcp_tools("memory", _FakeMemory())["memory.search"], payload)
    _record("f12b", "MemorySearchInput.agent_id", "MCP memory.search", obs)
    assert obs == "ValidationError"


# --------------------------------------------------------------------------- extractor (LLM output)


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


def _extract_obs(payload: dict) -> str:
    from pydantic import ValidationError

    try:
        ext = _extract(payload)
    except ValidationError:
        return "ValidationError"
    # Not rejected at the entry: show what the ingest pipeline does with it next.
    from graphrag_service.ingest.resolver import EntityResolver
    from graphrag_service.settings import GraphRAGSettings

    try:
        asyncio.run(EntityResolver(GraphRAGSettings()).resolve(ext.entities))
        for _r in ext.relations:
            pass
    except Exception as exc:
        return f"accepted; then {type(exc).__name__} in resolver/writer"
    return "accepted"


LLM_OK = {
    "entities": [
        {"name": "Fractions", "kind": "Concept", "confidence": 0.9},
        {"name": "Division", "kind": "Concept", "confidence": 0.8},
    ],
    "relations": [{"src_name": "Division", "dst_name": "Fractions", "kind": "PREREQUISITE_OF"}],
    "claims": [],
    "confidence": 0.8,
}


def test_f10_extraction_entities_omitted() -> None:
    obs = _extract_obs({k: v for k, v in LLM_OK.items() if k != "entities"})
    _record("f10", "Extraction.entities", "Extractor.extract (LLM JSON -> Extraction)", obs)
    assert obs == "ValidationError"


def test_f11_extraction_relations_omitted() -> None:
    obs = _extract_obs({k: v for k, v in LLM_OK.items() if k != "relations"})
    _record("f11", "Extraction.relations", "Extractor.extract (LLM JSON -> Extraction)", obs)
    assert obs == "ValidationError"


# ------------------------------------------------------- raw dicts / Relation.weight


def _write(ext):
    from graphrag_service.default_service import DefaultGraphRAGService
    from graphrag_service.ingest.resolver import EntityResolver
    from graphrag_service.ingest.types import RawDocument
    from graphrag_service.ingest.writer import GraphWriter
    from graphrag_service.settings import GraphRAGSettings
    from schemas.common import Provenance

    svc = DefaultGraphRAGService()
    doc = RawDocument(id="doc1", title="t", text="x", source=Provenance(kind="import", id="doc1"))

    async def run():
        resolved = await EntityResolver(GraphRAGSettings()).resolve(ext.entities)
        return await GraphWriter(svc).write_extraction(ext, resolved, doc=doc, chunk_ids=[])

    return svc, asyncio.run(run())


def test_x01_extraction_llm_raw_dicts_coerced_before_resolver_writer() -> None:
    """LLM-shaped JSON: entities/relations arrive as dicts and must reach the resolver
    and writer as Entity/Relation models (tip: dicts -> AttributeError in the resolver)."""
    from schemas.graph import EdgeKind, Entity, NodeKind, Relation

    ext = _extract(LLM_OK)
    assert all(isinstance(e, Entity) for e in ext.entities)
    assert all(isinstance(r, Relation) for r in ext.relations)
    assert ext.entities[0].kind is NodeKind.CONCEPT
    svc, (nodes, edges, _pending) = _write(ext)
    assert (nodes, edges) == (2, 1)
    (edge,) = svc._edges.values()
    assert edge.kind is EdgeKind.PREREQUISITE_OF and edge.weight == 1.0


def test_x02_extraction_llm_unknown_kind_rejected() -> None:
    from pydantic import ValidationError

    bad = json.loads(json.dumps(LLM_OK))
    bad["entities"][0]["kind"] = "banana"
    with pytest.raises(ValidationError):
        _extract(bad)


def test_x03_writer_relation_weight_unset_uses_pre_as90_default() -> None:
    """writer.py:68 reads relation.weight; the heuristic extractor never sets it.
    Pre-AS-90 default was 1.0 (tip: None, and an undeclared FlexibleModel read)."""
    from schemas.graph import EdgeKind, Entity, Extraction, NodeKind, Relation

    ext = Extraction(
        entities=[
            Entity(name="Division", kind=NodeKind.CONCEPT, confidence=0.9),
            Entity(name="Fractions", kind=NodeKind.CONCEPT, confidence=0.9),
        ],
        relations=[
            Relation(
                src_name="Division",
                dst_name="Fractions",
                kind=EdgeKind.PREREQUISITE_OF,
                confidence=0.6,
            )
        ],
        claims=[],
        confidence=0.6,
    )
    svc, (_n, edges, _p) = _write(ext)
    assert edges == 1
    (edge,) = svc._edges.values()
    assert edge.weight == 1.0
