"""AS-99: regressions behind the pre-existing memory / graphrag / apps/api failures.

Fakes only: no network, no DB, no keys. The service suites themselves
(services/memory/tests, services/graphrag/tests, apps/api/tests) are not part of the
root pytest run, so these pin the underlying fixes from the root.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _rel in ("services/memory", "services/graphrag"):
    if str(ROOT / _rel) not in sys.path:
        sys.path.insert(0, str(ROOT / _rel))

from schemas import errors  # noqa: E402
from schemas.graph import EdgeKind, KGNode, NodeKind  # noqa: E402
from schemas.memory import MemoryRecord  # noqa: E402


@pytest.mark.parametrize(
    ("name", "status", "code"),
    [
        ("AppError", 500, "app_error"),
        ("AuthError", 401, "auth_error"),
        ("ForbiddenError", 403, "forbidden"),
        ("NotFoundError", 404, "not_found"),
        ("ValidationFailed", 422, "validation_failed"),
        ("PolicyViolation", 403, "policy_violation"),
        ("RateLimited", 429, "rate_limited"),
        ("UpstreamError", 502, "upstream_error"),
        ("BudgetExceeded", 402, "budget_exceeded"),
    ],
)
def test_app_errors_carry_http_mapping(name: str, status: int, code: str) -> None:
    cls = getattr(errors, name)
    assert issubclass(cls, errors.AppError)
    exc = cls("boom")
    assert exc.http_status == status
    assert exc.to_dict() == {"code": code, "message": "boom"}
    assert cls("x", code="custom").to_dict()["code"] == "custom"


def test_unknown_error_name_is_still_an_app_error() -> None:
    assert issubclass(errors.SomeFutureError, errors.AppError)


def test_graph_enums_have_the_members_production_uses() -> None:
    for member in ("LEARNER", "CONCEPT", "SKILL", "TOPIC", "LESSON", "RESOURCE", "MISCONCEPTION"):
        assert member in NodeKind.__members__
    assert NodeKind.CONCEPT.value == "Concept"
    for member in ("PREREQUISITE_OF", "TEACHES", "COVERS", "MASTERS", "OPPOSES", "DERIVED_FROM"):
        assert EdgeKind[member].value == member
    assert EdgeKind("PREREQUISITE_OF") is EdgeKind.PREREQUISITE_OF


def test_memory_record_scores_default_to_table_defaults() -> None:
    rec = MemoryRecord(id="m", learner_id="l", content="c")
    assert (rec.salience, rec.confidence, rec.decay_tau_days) == (0.5, 0.5, 14.0)
    # AS-90 fields keep their None default (output parity).
    assert rec.access_count is None and rec.kg_node_ids is None


def test_reinforce_handles_unset_access_count() -> None:
    from memory_service.hygiene.decay import reinforce, strength_now

    rec = reinforce(MemoryRecord(id="m", learner_id="l", content="c"))
    assert rec.access_count == 1
    assert strength_now(rec) > 0


@pytest.mark.asyncio
async def test_resolver_tolerates_nodes_without_aliases() -> None:
    from graphrag_service.ingest.resolver import EntityResolver
    from graphrag_service.settings import GraphRAGSettings
    from schemas.graph import Entity

    resolver = EntityResolver(GraphRAGSettings(), store=None)
    node = KGNode(id="concept:fractions", kind=NodeKind.CONCEPT, canonical_name="Fractions")
    assert node.aliases is None
    resolver.seed_memory({node.id: node})
    entity = Entity(name="Fractions", kind=NodeKind.CONCEPT, confidence=0.9)
    [out] = await resolver.resolve([entity])
    assert out.linked and out.node.id == "concept:fractions"
