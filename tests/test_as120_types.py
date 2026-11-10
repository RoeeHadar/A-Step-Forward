"""AS-120: the 31 type/enum/format diffs vs 3b7d2774 (items/AS-119 bounds diff --info).

Each case is one diff row: a value the tip accepted (the field was Any or a widened
enum) that the ref rejects. After AS-120 the entry-point model rejects it again, while
a valid control value is still accepted. Models are resolved by name, so the same
cases can be replayed against the ref schemas (items/AS-120/tools/ref_check.py).
"""

from __future__ import annotations

import copy
import importlib
from typing import Any

import pytest
from pydantic import ValidationError

_PROV = {"kind": "chat"}
_WRITE = {"learner_id": "l1", "type": "episodic", "content": "c", "provenance": _PROV}
_SEARCH = {"agent_id": "a1", "learner_id": "l1", "query": "q"}
_PROFILE = {"goal": "g", "subjects": ["math"], "hours_per_week": 5}
_EXTRACT = {
    "entities": [{"name": "A", "kind": "Concept"}],
    "relations": [{"src_name": "A", "dst_name": "B", "kind": "TEACHES"}],
}

# (module, model on tip/after, model on the ref 3b7d2774)
HYBRID = ("schemas.graph", "KGHybridBody", "KGHybridInput", {"query": "q"})
KSEARCH = ("schemas.graph", "KGSearchBody", "KGSearchInput", {"query": "q"})
WALK = ("schemas.graph", "KGWalkBody", "KGWalkInput", {"seed_node_ids": ["n1"]})
MWRITE = ("schemas.memory", "MemoryWriteBody", "MemoryWriteInput", _WRITE)
MTOOL = (
    "schemas.memory",
    "MemoryWriteToolBody",
    "MemoryWriteToolInput",
    {"agent_id": "a1", "input": _WRITE},
)
MSEARCH = ("schemas.memory", "MemorySearchBody", "MemorySearchInput", _SEARCH)
PROFILE = ("schemas.learner_model", "LearnerProfileBody", "LearnerProfileInput", _PROFILE)
EXTRACT = ("schemas.graph", "ExtractionPayload", "Extraction", _EXTRACT)

TS = "2026-12-01T00:00:00Z"

# id (= row in the AS-119 --info list), entry point, model, path, bad (tip ok, ref rejects), good
CASES: list[tuple[int, str, tuple, tuple, Any, Any]] = [
    (1, "HTTP POST /v1/graphrag/hybrid body.k type", HYBRID, ("k",), "ten", 5),
    (
        2,
        "HTTP POST /v1/graphrag/search body.kinds type",
        KSEARCH,
        ("kinds",),
        "Concept",
        ["Concept"],
    ),
    (3, "HTTP POST /v1/graphrag/search body.kinds[] type", KSEARCH, ("kinds",), [1], ["Skill"]),
    (
        4,
        "HTTP POST /v1/graphrag/search body.kinds[] enum",
        KSEARCH,
        ("kinds",),
        ["source"],
        ["Topic"],
    ),
    (5, "HTTP POST /v1/memory body.expires_at format", MWRITE, ("expires_at",), "next week", TS),
    (
        6,
        "HTTP POST /v1/memory body.provenance.model_version type",
        MWRITE,
        ("provenance", "model_version"),
        3,
        "v1",
    ),
    (7, "HTTP POST /v1/memory body.provenance.ts type", MWRITE, ("provenance", "ts"), [], TS),
    (
        8,
        "HTTP POST /v1/memory body.provenance.ts format",
        MWRITE,
        ("provenance", "ts"),
        "yesterday",
        TS,
    ),
    (
        9,
        "HTTP POST /v1/memory/search body.include_archived type",
        MSEARCH,
        ("include_archived",),
        "maybe",
        True,
    ),
    (
        10,
        "HTTP POST /v1/onboarding/submit body.background_notes type",
        PROFILE,
        ("background_notes",),
        12,
        "n",
    ),
    (
        11,
        "HTTP POST /v1/onboarding/submit body.grade_level type",
        PROFILE,
        ("grade_level",),
        12,
        "12",
    ),
    (
        12,
        "HTTP POST /v1/onboarding/submit body.points_group type",
        PROFILE,
        ("points_group",),
        5,
        "5",
    ),
    (
        13,
        "HTTP POST /v1/onboarding/submit body.preferred_style type",
        PROFILE,
        ("preferred_style",),
        1,
        "visual",
    ),
    (
        14,
        "HTTP POST /v1/onboarding/submit body.self_scores type",
        PROFILE,
        ("self_scores",),
        "high",
        {"limits": 3},
    ),
    (
        15,
        "HTTP POST /v1/onboarding/submit body.self_scores{} type",
        PROFILE,
        ("self_scores",),
        {"limits": "high"},
        {"limits": 3},
    ),
    (
        16,
        "LLM extractor .entities[].kind enum",
        EXTRACT,
        ("entities", 0, "kind"),
        "source",
        "Skill",
    ),
    (17, "LLM extractor .notes type", EXTRACT, ("notes",), 1, ""),
    (18, "LLM extractor .notes enum", EXTRACT, ("notes",), "maybe", "low_confidence"),
    (
        19,
        "LLM extractor .relations[].kind enum",
        EXTRACT,
        ("relations", 0, "kind"),
        "related_to",
        "PREREQUISITE_OF",
    ),
    (20, "MCP kg.hybrid .k type", HYBRID, ("k",), "ten", 5),
    (21, "MCP kg.search .kinds type", KSEARCH, ("kinds",), "Concept", ["Concept"]),
    (22, "MCP kg.search .kinds[] type", KSEARCH, ("kinds",), [1], ["Skill"]),
    (23, "MCP kg.search .kinds[] enum", KSEARCH, ("kinds",), ["source"], ["Topic"]),
    (24, "MCP kg.walk .edge_kinds type", WALK, ("edge_kinds",), "TEACHES", ["TEACHES"]),
    (25, "MCP kg.walk .edge_kinds[] type", WALK, ("edge_kinds",), [1], ["COVERS"]),
    (
        26,
        "MCP kg.walk .edge_kinds[] enum",
        WALK,
        ("edge_kinds",),
        ["prerequisite"],
        ["PREREQUISITE_OF"],
    ),
    (27, "MCP memory.search .include_archived type", MSEARCH, ("include_archived",), "maybe", True),
    (
        28,
        "MCP memory.write .input.expires_at format",
        MTOOL,
        ("input", "expires_at"),
        "next week",
        TS,
    ),
    (
        29,
        "MCP memory.write .input.provenance.model_version type",
        MTOOL,
        ("input", "provenance", "model_version"),
        3,
        "v1",
    ),
    (
        30,
        "MCP memory.write .input.provenance.ts type",
        MTOOL,
        ("input", "provenance", "ts"),
        [],
        TS,
    ),
    (
        31,
        "MCP memory.write .input.provenance.ts format",
        MTOOL,
        ("input", "provenance", "ts"),
        "yesterday",
        TS,
    ),
]


def payload(base: dict[str, Any], path: tuple, value: Any) -> dict[str, Any]:
    data = copy.deepcopy(base)
    node: Any = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return data


def model(spec: tuple, ref: bool = False) -> Any:
    module, tip_name, ref_name, _ = spec
    return getattr(importlib.import_module(module), ref_name if ref else tip_name)


def accepts(cls: Any, data: dict[str, Any]) -> bool:
    try:
        cls.model_validate(data)
    except ValidationError:
        return False
    return True


@pytest.mark.parametrize(
    ("case_id", "entry", "spec", "path", "bad", "good"), CASES, ids=[f"d{c[0]:02d}" for c in CASES]
)
def test_restored_type_rejects_tip_value(case_id, entry, spec, path, bad, good) -> None:
    cls = model(spec)
    assert accepts(cls, payload(spec[3], path, good)), f"{entry}: valid control rejected"
    assert not accepts(cls, payload(spec[3], path, bad)), f"{entry}: {bad!r} accepted (tip-widened)"


def test_restored_values_keep_service_types() -> None:
    """Accepted values reach the services as before: ISO strings stay strings, kinds are
    the shared enums, and provenance model_version/ts stay extras (stored unchanged)."""
    from schemas.graph import EdgeKind, ExtractionPayload, KGSearchBody, NodeKind
    from schemas.memory import MemoryWriteBody

    w = MemoryWriteBody.model_validate(
        payload(
            payload(_WRITE, ("expires_at",), TS),
            ("provenance",),
            {"kind": "chat", "ts": TS, "model_version": "v1"},
        )
    )
    assert w.expires_at == TS
    assert w.provenance.model_extra == {"ts": TS, "model_version": "v1"}
    assert w.provenance.model_dump(exclude_none=True) == {
        "kind": "chat",
        "ts": TS,
        "model_version": "v1",
    }
    s = KGSearchBody.model_validate({"query": "q", "kinds": ["Concept"]})
    assert s.kinds == [NodeKind.CONCEPT] and type(s.kinds[0]) is NodeKind
    e = ExtractionPayload.model_validate(_EXTRACT)
    assert type(e.entities[0].kind) is NodeKind and type(e.relations[0].kind) is EdgeKind
    assert e.notes == ""
