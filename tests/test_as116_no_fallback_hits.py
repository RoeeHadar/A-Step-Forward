"""AS-116: CI enforcement for the AS-90 FlexibleModel fallback guard.

AS-118 made the root conftest's reporter report-only, so it no longer sets the
exit status. This module restores enforcement through ordinary test failures:

* ``test_session_recorded_no_fallback_hits`` reads the reporter's live hit store,
  the ``as90_fallback_hits`` fixture from the root conftest. The conftest's
  ``pytest_collection_modifyitems`` moves this test to the end of the session, so
  when it runs as part of the full pytest it covers every test that ran before
  it. If any hit was recorded, it fails like any other test (rc 1). The exit
  status itself is never overridden.
* ``test_resolver_reads_declared_entity_fields`` drives the known trigger
  (graphrag ingest/resolver.py:72-73) directly. The check therefore also means
  something when this file runs on its own.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _rel in ("packages/schemas", "services/graphrag"):
    _p = str(_ROOT / _rel)
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _resolve(entity):
    from graphrag_service.ingest.resolver import EntityResolver
    from graphrag_service.settings import GraphRAGSettings

    return asyncio.run(EntityResolver(GraphRAGSettings(), store=None)._resolve_one(entity))


@pytest.mark.parametrize("payload", [False, True], ids=["Entity", "EntityPayload"])
def test_resolver_reads_declared_entity_fields(payload: bool, as90_fallback_hits) -> None:
    from schemas.graph import Entity, EntityPayload, NodeKind

    cls = EntityPayload if payload else Entity
    before = dict(as90_fallback_hits)
    given = _resolve(
        cls(
            name="Fractions",
            kind=NodeKind.CONCEPT,
            aliases=["parts"],
            description="d",
            confidence=0.9,
        )
    )
    default = _resolve(cls(name="Ratios", kind=NodeKind.CONCEPT, confidence=0.9))
    assert dict(as90_fallback_hits) == before, "resolver read an undeclared Entity field"
    assert (given.node.aliases, given.node.summary) == (["parts"], "d")
    # Pre-AS-90 defaults (3b7d2774): aliases=[] and description=None reach the node.
    assert (default.node.aliases, default.node.summary) == ([], None)


def test_session_recorded_no_fallback_hits(as90_fallback_hits) -> None:
    hits = [f"{c}.{f} {loc} x{n}" for (c, f, loc), n in sorted(as90_fallback_hits.items())]
    assert not hits, "AS-90 fallback reads from production code:\n  " + "\n  ".join(hits)
