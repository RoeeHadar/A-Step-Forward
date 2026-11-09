"""AS-110: production reads of AS-90 None-default fields guarded with pre-AS-90 defaults.

Every model here is built with the guarded field left unset (so it is ``None``) and the
read site is exercised. Fakes only: no network, no DB, no Neo4j, no keys. On the base
tree (b52e4cd6) each test crashes on ``None`` or returns the wrong result.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _rel in ("services/memory", "services/graphrag", "services/learner_model"):
    if str(ROOT / _rel) not in sys.path:
        sys.path.insert(0, str(ROOT / _rel))

from schemas.common import Provenance  # noqa: E402
from schemas.graph import (  # noqa: E402
    EdgeKind,
    Extraction,
    KGEdge,
    KGHybridInput,
    KGNode,
    KGSearchInput,
    KGWalkInput,
    NodeKind,
)
from schemas.learner_model import LearnerProfileInput  # noqa: E402
from schemas.memory import MemoryRecord, MemorySearchInput, MemoryType  # noqa: E402


# --- memory: retrieval.hybrid.hybrid_search (MemorySearchInput.min_strength / k) ---------


class _MemRepo:
    def __init__(self, n: int) -> None:
        self.rows = [
            MemoryRecord(
                id=f"m{i}",
                learner_id="l1",
                type=MemoryType.SEMANTIC,
                content=f"fractions note {i}",
                provenance=Provenance(kind="system", id="t"),
            )
            for i in range(n)
        ]

    async def iter_for_learner(self, learner_id: str):
        return [r for r in self.rows if r.learner_id == learner_id]


@pytest.mark.asyncio
async def test_memory_hybrid_search_min_strength_unset() -> None:
    from memory_service.retrieval.hybrid import hybrid_search

    # Same shape as apps/api routers/memory.py list(q=...): no min_strength.
    inp = MemorySearchInput(learner_id="l1", query="fractions", k=5)
    assert inp.min_strength is None
    out = await hybrid_search(_MemRepo(3), inp)
    assert len(out) == 3


@pytest.mark.asyncio
async def test_memory_hybrid_search_k_unset_defaults_to_10() -> None:
    from memory_service.retrieval.hybrid import hybrid_search

    inp = MemorySearchInput(learner_id="l1", query="fractions", min_strength=0.0)
    assert inp.k is None
    out = await hybrid_search(_MemRepo(12), inp)
    assert len(out) == 10


# --- graphrag: in-memory DefaultGraphRAGService (KGSearchInput.k, KGWalkInput.depth/limit,
#     KGHybridInput.k/depth) ---------------------------------------------------------------


async def _graph(n_nodes: int):
    from graphrag_service.default_service import DefaultGraphRAGService

    svc = DefaultGraphRAGService()
    for i in range(n_nodes):
        await svc.upsert_node(
            KGNode(id=f"concept:f{i}", kind=NodeKind.CONCEPT, canonical_name=f"Fractions {i}")
        )
    await svc.upsert_edge(
        KGEdge(id="e1", kind=EdgeKind.PREREQUISITE_OF, src="concept:f0", dst="concept:f1")
    )
    return svc


@pytest.mark.asyncio
async def test_graph_search_k_unset_defaults_to_10() -> None:
    svc = await _graph(12)
    inp = KGSearchInput(query="fractions")
    assert inp.k is None
    assert len(await svc.search(inp)) == 10


@pytest.mark.asyncio
async def test_graph_walk_depth_and_limit_unset() -> None:
    svc = await _graph(2)
    inp = KGWalkInput(seed_node_ids=[f"concept:f{i % 2}" for i in range(60)])
    assert inp.depth is None and inp.limit is None
    paths = await svc.walk(inp)
    assert len(paths) == 50  # pre-AS-90 limit default
    # depth 2 from concept:f0 reaches concept:f1 over the prerequisite edge
    assert [n.id for n in paths[0].nodes] == ["concept:f0", "concept:f1"]


@pytest.mark.asyncio
async def test_graph_hybrid_k_and_depth_unset() -> None:
    svc = await _graph(12)
    inp = KGHybridInput(query="fractions")
    assert inp.k is None and inp.depth is None
    assert len(await svc.hybrid(inp)) == 10


# --- graphrag: Neo4j query layer retrieval/queries.py, with fake store/chunks/embedder -----


class _FakeEmbedder:
    async def embed_texts(self, texts):
        return [[0.0, 1.0] for _ in texts]


class _FakeChunks:
    def __init__(self) -> None:
        self.k = "unset"

    async def vector_search(self, _emb, *, k):
        self.k = k
        return []


class _FakeStore:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def fulltext_search(self, q, *, k, kinds=None):
        self.calls.append({"fulltext_k": k})
        return [(KGNode(id="concept:a", kind=NodeKind.CONCEPT, canonical_name="A"), 0.6)]

    async def walk(self, seeds, *, depth, edge_kinds=None, limit=50):
        self.calls.append({"depth": depth, "limit": limit})
        return []


@pytest.mark.asyncio
async def test_queries_local_search_k_unset() -> None:
    from graphrag_service.retrieval import queries

    chunks, store = _FakeChunks(), _FakeStore()
    await queries.local_search(store, chunks, _FakeEmbedder(), KGSearchInput(query="a"))
    assert chunks.k == 10 and store.calls == [{"fulltext_k": 10}]


@pytest.mark.asyncio
async def test_queries_graph_walk_depth_limit_unset() -> None:
    from graphrag_service.retrieval import queries

    store = _FakeStore()
    await queries.graph_walk(store, KGWalkInput(seed_node_ids=["concept:a"]))
    assert store.calls == [{"depth": 2, "limit": 50}]


@pytest.mark.asyncio
async def test_queries_hybrid_k_depth_unset() -> None:
    from graphrag_service.retrieval import queries

    chunks, store = _FakeChunks(), _FakeStore()
    out = await queries.hybrid_search(store, chunks, _FakeEmbedder(), KGHybridInput(query="a"))
    assert [r.node.id for r in out] == ["concept:a"]
    assert store.calls[-1] == {"depth": 2, "limit": 30}


# --- graphrag: ingest.verifier (Extraction.confidence) -------------------------------------


@pytest.mark.asyncio
async def test_verifier_extraction_confidence_unset() -> None:
    from graphrag_service.ingest.verifier import Verifier

    ext = Extraction(notes="", claims=[])  # e.g. an LLM extraction without "confidence"
    assert ext.confidence is None
    result = await Verifier(sample_rate=1.0).verify(ext)
    assert result.flagged == 0  # pre-AS-90 default 0.5 is not < 0.5


# --- graphrag: stores.neo4j_store upsert_node / upsert_edge params ------------------------


class _FakeSession:
    def __init__(self, sink: list) -> None:
        self.sink = sink

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc) -> None:
        return None

    async def run(self, _cypher, params):
        self.sink.append(params)


def _store():
    from graphrag_service.settings import GraphRAGSettings
    from graphrag_service.stores.neo4j_store import Neo4jStore

    store = Neo4jStore(GraphRAGSettings())
    sink: list = []
    store._session = lambda: _FakeSession(sink)  # type: ignore[method-assign]
    return store, sink


@pytest.mark.asyncio
async def test_neo4j_upsert_node_unset_fields() -> None:
    store, sink = _store()
    # Same shape as ingest/writer.py chunk nodes: aliases/properties/created_at unset.
    node = KGNode(id="chunk:1", kind=NodeKind.RESOURCE, canonical_name="Chunk 1")
    assert node.created_at is None and node.aliases is None
    await store.upsert_node(node)
    p = sink[0]
    assert json.loads(p["aliases"]) == [] and json.loads(p["properties"]) == {}
    assert p["pending_review"] is False and p["created_at"].endswith("+00:00")


@pytest.mark.asyncio
async def test_neo4j_upsert_edge_unset_fields() -> None:
    store, sink = _store()
    edge = KGEdge(id="e", kind=EdgeKind.DERIVED_FROM, src="a", dst="b")
    assert edge.weight is None and edge.properties is None
    await store.upsert_edge(edge)
    assert sink[0]["weight"] == 1.0 and json.loads(sink[0]["properties"]) == {}


# --- learner_model: create_profile (LearnerProfileInput.self_scores) ----------------------


def _profile_input() -> LearnerProfileInput:
    inp = LearnerProfileInput(goal="Pass Bagrut", subjects=["math"], hours_per_week=4)
    assert inp.self_scores is None
    return inp


@pytest.mark.asyncio
async def test_learner_default_service_create_profile_self_scores_unset() -> None:
    from learner_model_service.default_service import DefaultLearnerModelService

    out = await DefaultLearnerModelService().create_profile("l1", _profile_input())
    assert out.learner_id == "l1"


class _FakeResult:
    def __init__(self, row) -> None:
        self.row = row

    def scalar_one_or_none(self):
        return self.row


class _FakeDBSession:
    def __init__(self) -> None:
        self.executed = 0
        self.row = SimpleNamespace(
            learner_id="l1", goal="Pass Bagrut", grade_level=None, points_group=None,
            subjects=["math"], hours_per_week=4, preferred_style=None, attention_span=None,
            self_scores=None, background_notes=None, created_at=None, updated_at=None,
        )

    async def execute(self, _stmt):
        self.executed += 1
        return _FakeResult(self.row)

    async def commit(self) -> None:
        return None


@pytest.mark.asyncio
async def test_learner_repository_create_profile_self_scores_unset() -> None:
    from learner_model_service.settings import LearnerModelSettings
    from learner_model_service.stores.repository import LearnerModelRepository

    session = _FakeDBSession()
    repo = LearnerModelRepository(LearnerModelSettings(), session=session)  # type: ignore[arg-type]
    out = await repo.create_profile("l1", _profile_input())
    assert out.learner_id == "l1" and session.executed == 2  # upsert + read-back, no mastery
