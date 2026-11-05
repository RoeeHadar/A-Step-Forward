"""AS-90 r1: capture the JSON that production sites emit, from fixed fakes.

Run on any tree (base 5d1d9b63, r0, r1); output must be identical to the
base fixture tests/fixtures/as90_base_output.json. No network, no DB.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
for rel in (
    "packages/schemas",
    "packages/agents",
    "services/memory",
    "services/graphrag",
    "services/orchestrator",
    "services/diagnostic",
    "services/learning_path",
    "services/learner_model",
    "services/curriculum",
    "apps/api",
):
    p = str(ROOT / rel)
    if p not in sys.path:
        sys.path.insert(0, p)

T0 = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def _provenances() -> dict[str, Any]:
    """Provenance built exactly as each production source builds it."""
    from schemas.common import Provenance

    return {
        # graphrag ingest/writer.py:96 and sources/*.py
        "writer": Provenance(kind="import", id="doc-1"),
        # orchestrator/episodic.py:60
        "episodic": Provenance(kind="chat", id="turn-1", agent="tutor"),
        # agents/base/skill_accumulator.py:62
        "skill_accumulator": Provenance(kind="agent_reflection", id="tutor", agent="tutor"),
        # memory hygiene/dreaming.py:106 (model set explicitly)
        "dreaming": Provenance(kind="agent_reflection", id="dreamer", agent="dreamer", model="m"),
        # round-trip from a stored row without id/model keys
        "stored_raw": Provenance.model_validate({"kind": "chat", "agent": "tutor"}),
    }


def _memory_record(prov: Any) -> Any:
    """MemoryRecord as memory_service/default_service.py:46 builds it."""
    from schemas.memory import MemoryRecord, MemoryType

    return MemoryRecord(
        id="mem-1",
        learner_id="learner-1",
        type=MemoryType.EPISODIC,
        content="c",
        summary="s",
        tags=["chat"],
        valence=0.0,
        salience=0.5,
        confidence=0.5,
        decay_tau_days=30.0,
        provenance=prov,
        expires_at=None,
        created_at=T0,
        updated_at=T0,
        last_accessed_at=T0,
    )


def _route(router: Any, path: str, method: str) -> Any:
    for r in router.routes:
        if r.path == path and method in r.methods:
            return r
    raise LookupError(path)


async def _serialize(route: Any, content: Any) -> Any:
    """Serialize exactly as FastAPI does for this route's response_model."""
    from fastapi.routing import serialize_response
    from starlette.responses import Response

    if isinstance(content, Response):  # endpoint returned a Response itself
        return json.loads(content.body)
    return await serialize_response(
        field=route.response_field,
        response_content=content,
        include=route.response_model_include,
        exclude=route.response_model_exclude,
        by_alias=route.response_model_by_alias,
        exclude_unset=route.response_model_exclude_unset,
        exclude_defaults=route.response_model_exclude_defaults,
        exclude_none=route.response_model_exclude_none,
        is_coroutine=True,
    )


async def _writers(out: dict[str, Any]) -> None:
    from graphrag_service.stores import chunk_repository, neo4j_store
    from memory_service.stores import mappers, type_repositories
    from schemas.graph import KGChunk

    for name, prov in _provenances().items():
        rec = _memory_record(prov)
        # memory_service/stores/mappers.py:79
        row = mappers.record_to_row(rec)
        out[f"writer.mappers.{name}"] = row.provenance
        # memory_service/stores/type_repositories.py:175 (_apply_record)
        fake_row = SimpleNamespace()
        type_repositories.TypedMemoryRepository._apply_record(None, fake_row, rec, embedding=None)  # type: ignore[arg-type]
        out[f"writer.type_repositories.{name}"] = fake_row.provenance
        # graphrag/stores/neo4j_store.py:22
        out[f"writer.neo4j_store.{name}"] = json.loads(
            neo4j_store._serialize_provenance(prov) or "null"
        )
        # graphrag/stores/chunk_repository.py:72 (postgres branch, fake session)
        captured: dict[str, Any] = {}

        class _S:
            async def __aenter__(self) -> _S:
                return self

            async def __aexit__(self, *a: Any) -> None:
                return None

            async def execute(self, _q: Any, params: dict[str, Any]) -> None:
                captured.update(params)  # noqa: B023 - fake consumed within the same iteration

            async def commit(self) -> None:
                return None

        repo = chunk_repository.ChunkRepository.__new__(chunk_repository.ChunkRepository)
        repo.settings = SimpleNamespace(embedding_dim=2)
        repo._use_postgres = True
        repo._memory = {}
        repo._engine = object()
        repo._sessionmaker = lambda: _S()
        chunk = KGChunk(id="ch-1", document_id="doc-1", ordinal=0, text="t", provenance=prov)
        await repo.upsert(chunk)
        p = captured.get("provenance")
        out[f"writer.chunk_repository.{name}"] = json.loads(p) if isinstance(p, str) else p


async def _call(route: Any, **kwargs: Any) -> Any:
    """Invoke the real endpoint function, then serialize as FastAPI would."""
    content = await route.endpoint(**kwargs)
    return await _serialize(route, content)


async def _endpoints(out: dict[str, Any]) -> None:
    from agents import AGENT_REGISTRY
    from agents.base.tools import local_tool, mcp_tool
    from app.core.auth import AuthCtx
    from app.routers import agents as r_agents
    from app.routers import diagnostic as r_diag
    from app.routers import learners as r_learners
    from app.routers import learning_path as r_lp
    from app.routers import memory as r_mem
    from app.routers import progress as r_prog
    from app.services.learner import LearnerService
    from app.services.progress_svc import ProgressService
    from memory_service.stores import mappers
    from schemas.agents import ToolRef
    from schemas.diagnostic import DiagnosticAnswerResponse, DiagnosticQuestion
    from schemas.learning_path import QuizSubmitResponse
    from schemas.memory import MemorySearchResult, MemoryType

    ctx = AuthCtx(learner_id="learner-1")

    rt = _route(r_learners.router, "/v1/learners/me", "GET")
    lsvc = LearnerService()
    out["endpoint.learners_me.new"] = await _call(rt, ctx=ctx, svc=lsvc, _=None)
    out["endpoint.learners_me.cached"] = await _call(
        rt, ctx=AuthCtx(learner_id="learner-1", age=9), svc=lsvc, _=None
    )
    # learner.py:42 set_role path (no AS-90 fields set), then served by /me
    await lsvc.set_role("learner-2", lsvc._profiles["learner-1"].role)
    lsvc._profiles["learner-2"] = lsvc._profiles["learner-2"]

    class _CachedOnly:
        async def get_or_create(self, c: Any) -> Any:
            return lsvc._profiles[c.learner_id]

    out["endpoint.learners_me.set_role"] = await _call(
        rt, ctx=AuthCtx(learner_id="learner-2"), svc=_CachedOnly(), _=None
    )

    rt = _route(r_prog.router, "/v1/progress", "GET")
    out["endpoint.progress"] = await _call(rt, ctx=ctx, svc=ProgressService(), _=None)

    for name, prov in _provenances().items():
        rec = _memory_record(prov)
        stored = mappers.row_to_record(mappers.record_to_row(rec), MemoryType.EPISODIC)

        class _Mem:
            async def write(self, *a: Any, **k: Any) -> Any:
                return rec  # noqa: B023 - fake consumed within the same iteration

            async def timeline(self, *a: Any, **k: Any) -> Any:
                return [stored]  # noqa: B023 - fake consumed within the same iteration

            async def search(self, *a: Any, **k: Any) -> Any:
                return [MemorySearchResult(record=stored, score=0.5)]  # noqa: B023 - fake consumed within the same iteration

            async def update(self, *a: Any, **k: Any) -> Any:
                return stored  # noqa: B023 - fake consumed within the same iteration

        m = _Mem()
        body = SimpleNamespace(learner_id="learner-1")
        out[f"endpoint.memory_post.{name}"] = await _call(
            _route(r_mem.router, "/v1/memory", "POST"), body=body, ctx=ctx, svc=m, _=None
        )
        out[f"endpoint.memory_list.{name}"] = await _call(
            _route(r_mem.router, "/v1/memory", "GET"), ctx=ctx, svc=m, q=None, k=10, _=None
        )
        out[f"endpoint.memory_list_q.{name}"] = await _call(
            _route(r_mem.router, "/v1/memory", "GET"), ctx=ctx, svc=m, q="x", k=10, _=None
        )
        out[f"endpoint.memory_search.{name}"] = await _call(
            _route(r_mem.router, "/v1/memory/search", "POST"), body=body, ctx=ctx, svc=m, _=None
        )
        out[f"endpoint.memory_timeline.{name}"] = await _call(
            _route(r_mem.router, "/v1/memory/timeline", "GET"), ctx=ctx, svc=m, k=10, _=None
        )
        out[f"endpoint.memory_patch.{name}"] = await _call(
            _route(r_mem.router, "/v1/memory/{memory_id}", "PATCH"),
            memory_id="mem-1",
            patch=None,
            ctx=ctx,
            svc=m,
            _=None,
        )

    rt = _route(r_diag.router, "/v1/diagnostic/{session_id}/answer", "POST")
    q = DiagnosticQuestion(id="1", topic="t", subject="s", difficulty=0.5, stem="?", options=[])
    # diagnostic postgres_service.py:114 and :133
    for name, resp in {
        "complete": DiagnosticAnswerResponse(
            complete=True,
            question_number=3,
            total_estimate=10,
            results={"mastery_by_topic": {"t": 0.5}, "responses": []},
        ),
        "next": DiagnosticAnswerResponse(
            complete=False, question=q, question_number=2, total_estimate=10
        ),
    }.items():

        class _Diag:
            async def answer(self, *a: Any, _r: Any = resp, **k: Any) -> Any:
                return _r

        out[f"endpoint.diagnostic_answer.{name}"] = await _call(
            rt, session_id="s", body=None, ctx=ctx, svc=_Diag(), _=None
        )

    rt = _route(r_lp.router, "/v1/learners/me/plans/{plan_id}/weeks/{week_num}/quiz/submit", "POST")
    # learning_path quiz_repository.py:148 and :207
    for name, resp in {
        "idempotent": QuizSubmitResponse(
            quiz_id="q", score=0.5, per_topic={"t": 0.5}, weak_concepts=["t"], plan_adapted=False
        ),
        "fresh": QuizSubmitResponse(
            quiz_id="q",
            score=0.5,
            per_topic={"t": 0.5},
            weak_concepts=["t"],
            plan_adapted=False,
            next_week_concepts=None,
        ),
    }.items():

        class _LP:
            async def start_quiz(self, *a: Any, **k: Any) -> Any:
                return SimpleNamespace(quiz_id="q")

            async def submit_quiz(self, *a: Any, _r: Any = resp, **k: Any) -> Any:
                return _r

        out[f"endpoint.quiz_submit.{name}"] = await _call(
            rt,
            plan_id="p",
            week_num=1,
            body=SimpleNamespace(answers=[]),
            ctx=ctx,
            svc=_LP(),
            _=None,
        )

    rt = _route(r_agents.router, "/v1/agents", "GET")
    out["endpoint.agents"] = await _call(rt, ctx=ctx, _=None)
    # ToolRef.transport: tools.py:13/18 set it; agents/__init__.py ToolRef(...) does not.
    first = next(iter(AGENT_REGISTRY))
    saved = dict(AGENT_REGISTRY)
    try:
        AGENT_REGISTRY.clear()
        AGENT_REGISTRY[first] = saved[first].model_copy(
            update={
                "tools": [
                    mcp_tool("memory", "memory.search"),
                    local_tool("x"),
                    ToolRef(server="m", name="n"),
                ]
            }
        )
        out["endpoint.agents.tool_helpers"] = await _call(rt, ctx=ctx, _=None)
    finally:
        AGENT_REGISTRY.clear()
        AGENT_REGISTRY.update(saved)
    _ = AGENT_REGISTRY


async def _chat(out: dict[str, Any]) -> None:
    """/v1/chat SSE stream (chat.py:99): chunks built as runner/graph/invoke build them."""
    from app.core.auth import AuthCtx
    from app.routers import chat as r_chat
    from schemas.agents import AgentName, ChatChunk, ChatRequest
    from schemas.common import Citation

    chunks = [
        ChatChunk(kind="token", agent=AgentName.TUTOR, text="hi"),
        ChatChunk(
            kind="citation",
            agent=AgentName.QA_EXPLAINER,
            citation=Citation(title="t", url="<redacted>", agent="qa"),
        ),
        ChatChunk(
            kind="citation",
            agent=AgentName.RESEARCH,
            citation=Citation(source_id="s1", source_kind="doc", quote="q", score=0.5),
        ),
        ChatChunk(kind="error", agent=AgentName.ORCHESTRATOR, text="Routing failed."),
        ChatChunk(kind="done", agent=AgentName.TUTOR),
    ]

    class _Runner:
        async def stream(self, *a: Any, **k: Any) -> Any:
            for c in chunks:
                yield c

    async def _no_persist(**k: Any) -> None:
        return None

    saved = r_chat.persist_memory_event
    r_chat.persist_memory_event = _no_persist
    try:
        rt = _route(r_chat.router, "/v1/chat", "POST")
        resp = await rt.endpoint(
            body=ChatRequest(learner_id="learner-1", message="hello"),
            ctx=AuthCtx(learner_id="learner-1"),
            runner=_Runner(),
            _=None,
        )
        events = []
        async for part in resp.body_iterator:
            text = part.decode() if isinstance(part, bytes) else part
            head, data = text.strip().split("\n", 1)
            events.append({"event": head, "data": json.loads(data.removeprefix("data: "))})
        await asyncio.sleep(0)
    finally:
        r_chat.persist_memory_event = saved
    out["endpoint.chat.sse"] = events


def capture() -> dict[str, Any]:
    out: dict[str, Any] = {}

    async def _run() -> None:
        await _writers(out)
        await _endpoints(out)
        await _chat(out)

    asyncio.run(_run())
    return out


if __name__ == "__main__":
    print(json.dumps(capture(), indent=1, sort_keys=True, default=str))
