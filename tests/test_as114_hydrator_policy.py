"""AS-114: the agent memory hydrator must return no memories, as on the pre-AS-90
reference 3b7d2774, while every other MemorySearchInput read path is unchanged.

On the ref, memory_hydrator.hydrate() built MemorySearchInput without agent_id;
agent_id was a required field there, so construction raised ValidationError inside
the hydrator's `try`, the `except Exception` swallowed it, memory_api.search was
never called and the hydrator returned an empty HydratedMemory (trace:
items/AS-114/logs/trace-ref-3b7d2774.log). After AS-90 the field defaults to None,
the search runs with the default read policy and memories come back.

Fakes only: a real DefaultMemoryService over an in-memory fake repository (audit
sink stubbed), no DB, no network, no keys. Each test records what it observed to
$AS114_OBS (JSON lines) so ref / tip / after runs can be compared.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _rel in ("packages/schemas", "packages/agents", "services/memory"):
    _p = str(_ROOT / _rel)
    if _p not in sys.path:
        sys.path.insert(0, _p)

LEARNER = "learner-as114"


def _record(test: str, case: str, returned: list[str], search_calls: int) -> None:
    out = os.environ.get("AS114_OBS")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            row = {
                "test": test,
                "case": case,
                "memories_returned": len(returned),
                "ids": returned,
                "search_calls": search_calls,
            }
            fh.write(json.dumps(row) + "\n")


def _records():
    from schemas.common import Provenance
    from schemas.memory import MemoryRecord, MemoryType

    now = datetime.now(UTC)
    common = dict(
        learner_id=LEARNER,
        salience=0.9,
        confidence=0.9,
        valence=0.0,
        decay_tau_days=14.0,
        last_accessed_at=now,
        created_at=now,
        updated_at=now,
        provenance=Provenance(kind="chat", id="turn-1"),
    )
    return [
        MemoryRecord(
            id="m-sem", type=MemoryType.SEMANTIC, content="likes fractions practice", **common
        ),
        MemoryRecord(
            id="m-aff", type=MemoryType.AFFECTIVE, content="frustrated with fractions", **common
        ),
    ]


class _FakeRepo:
    def __init__(self) -> None:
        self.rows = _records()

    async def iter_for_learner(self, learner_id):
        return [r for r in self.rows if r.learner_id == learner_id]

    async def reinforce(self, memory_id, *, learner_id):
        return None


class _CountingService:
    """Real DefaultMemoryService (hybrid_search + filter_by_policy) on a fake repo."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import memory_service.default_service as ds

        async def _no_audit(*_a, **_k):
            return None

        monkeypatch.setattr(ds, "audit_event", _no_audit)
        svc = ds.DefaultMemoryService.__new__(ds.DefaultMemoryService)
        svc.settings = SimpleNamespace()
        svc.repo = _FakeRepo()
        self._svc = svc
        self.search_calls = 0
        self.writes = 0

    async def search(self, inp):
        self.search_calls += 1
        return await self._svc.search(inp)

    async def write(self, *_a, **_k):  # maybe_write_skill in Agent.pre
        self.writes += 1
        return None


def _ids(results) -> list[str]:
    return sorted(r.record.id for r in results)


# --------------------------------------------------------------------------- hydrator


def test_h1_hydrate_returns_no_memories(monkeypatch: pytest.MonkeyPatch) -> None:
    from agents.base.memory_hydrator import hydrate

    api = _CountingService(monkeypatch)
    out = asyncio.run(hydrate(learner_id=LEARNER, query="fractions", memory_api=api))
    _record(
        "h1",
        "hydrate(learner_id, query, memory_api) with memories present",
        out.record_ids,
        api.search_calls,
    )
    assert out.record_ids == [] and out.summary == ""
    assert api.search_calls == 0  # as on the ref: the search is never reached


def test_h2_agent_pre_hydrated_memory_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """The only production caller: Agent.pre() stores hydrate()'s result in ctx.extra."""
    from agents.base.agent import Agent, AgentContext

    class _Safety:
        async def pre(self, **_k):
            return None

    agent = Agent.__new__(Agent)
    agent.name = "tutor"
    agent.safety = _Safety()
    api = _CountingService(monkeypatch)
    ctx = AgentContext(learner_id=LEARNER, session_id="s1", turn_id="t1", memory_api=api)
    asyncio.run(agent.pre("fractions", ctx))
    hydrated = ctx.extra["hydrated_memory"]
    _record(
        "h2",
        "Agent.pre -> ctx.extra['hydrated_memory'] (agent 'tutor')",
        hydrated.record_ids,
        api.search_calls,
    )
    assert hydrated.record_ids == [] and hydrated.summary == ""
    assert api.search_calls == 0


def test_h3_hydrate_with_explicit_agent_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """After AS-114 a caller that names the reading agent gets that agent's policy.
    No production caller does this. The ref/tip hydrate() has no agent_id parameter."""
    from agents.base.memory_hydrator import hydrate

    if "agent_id" not in inspect.signature(hydrate).parameters:
        pytest.skip("hydrate() has no agent_id parameter on this tree")
    api = _CountingService(monkeypatch)
    out = asyncio.run(
        hydrate(learner_id=LEARNER, query="fractions", memory_api=api, agent_id="tutor")
    )
    _record("h3", "hydrate(..., agent_id='tutor') opt-in", sorted(out.record_ids), api.search_calls)
    assert sorted(out.record_ids) == ["m-sem"] and api.search_calls == 1


# --------------------------------------------------------------------------- controls


def _direct(monkeypatch, agent_id: str):
    from schemas.memory import MemorySearchInput

    api = _CountingService(monkeypatch)
    res = asyncio.run(
        api.search(
            MemorySearchInput(
                learner_id=LEARNER, query="fractions", k=10, agent_id=agent_id, min_strength=0.0
            )
        )
    )
    return _ids(res), api.search_calls


def test_c1_direct_search_agent_tutor_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Direct MemorySearchInput read with agent_id set: tutor policy -> semantic only."""
    ids, n = _direct(monkeypatch, "tutor")
    _record("c1", "MemoryService.search(MemorySearchInput(agent_id='tutor'))", ids, n)
    assert ids == ["m-sem"]


def test_c2_direct_search_agent_mentor_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Direct read with agent_id set: mentor policy -> semantic + affective."""
    ids, n = _direct(monkeypatch, "mentor")
    _record("c2", "MemoryService.search(MemorySearchInput(agent_id='mentor'))", ids, n)
    assert ids == ["m-aff", "m-sem"]


def test_c3_direct_search_default_read_policy_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default read (agent id with no policy entry, e.g. the GET /v1/memory?q= route's
    'user:memory_inspector'): {semantic, episodic} -> semantic only."""
    ids, n = _direct(monkeypatch, "user:memory_inspector")
    _record(
        "c3",
        "MemoryService.search(MemorySearchInput(agent_id='user:memory_inspector')) default policy",
        ids,
        n,
    )
    assert ids == ["m-sem"]


def test_c4_hydrate_memory_api_none_unchanged() -> None:
    from agents.base.memory_hydrator import hydrate

    out = asyncio.run(hydrate(learner_id=LEARNER, query="fractions", memory_api=None))
    _record("c4", "hydrate(memory_api=None) offline path", out.record_ids, 0)
    assert out.record_ids == [] and out.summary == ""
