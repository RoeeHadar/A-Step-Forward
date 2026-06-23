"""Retrieval-time policy filter.

Applies the calling agent's `MemoryAccessPolicy` plus learner-level policies
(child mode, consent flags). Sub-agent 04 + 10 wire the real
agent-registry lookup and child-mode flag from the learner profile.
"""

from __future__ import annotations

from schemas.memory import MemorySearchResult, MemoryType

# Phase-0 default policies per agent. Sub-agent 03/04 should source these from
# `packages/agents/agents/__init__.AGENT_REGISTRY` instead.
_AGENT_READ_POLICY: dict[str, set[MemoryType]] = {
    "tutor": {MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.PROCEDURAL, MemoryType.REFLECTIVE},
    "qa_explainer": {MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.SOURCE},
    "coach": {MemoryType.SEMANTIC, MemoryType.PROCEDURAL, MemoryType.EPISODIC},
    "mentor": {MemoryType.SEMANTIC, MemoryType.AFFECTIVE, MemoryType.PROCEDURAL},
    "memory_steward": set(MemoryType),  # full
    "orchestrator": set(MemoryType),
    "safety_moderation": {MemoryType.AFFECTIVE, MemoryType.SEMANTIC},
}


def allowed_types(agent_id: str) -> set[MemoryType]:
    return _AGENT_READ_POLICY.get(agent_id, {MemoryType.SEMANTIC, MemoryType.EPISODIC})


def filter_by_policy(results: list[MemorySearchResult], *, agent_id: str) -> list[MemorySearchResult]:
    allowed = allowed_types(agent_id)
    return [r for r in results if r.record.type in allowed]
