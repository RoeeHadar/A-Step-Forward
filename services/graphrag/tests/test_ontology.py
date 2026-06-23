"""GraphRAG ontology schema tests."""

from __future__ import annotations

from graphrag_service.ontology import CYPHER_CONSTRAINTS, CYPHER_FULLTEXT_INDEXES, CYPHER_INDEXES


def test_constraints_cover_all_node_kinds() -> None:
    kinds = {
        "Learner",
        "Concept",
        "Skill",
        "Topic",
        "Course",
        "Lesson",
        "Resource",
        "Assessment",
        "Question",
        "Misconception",
        "Goal",
        "Event",
        "Agent",
    }
    found = set()
    for stmt in CYPHER_CONSTRAINTS:
        for kind in kinds:
            if f":{kind}" in stmt:
                found.add(kind)
    assert found == kinds


def test_indexes_present() -> None:
    assert len(CYPHER_INDEXES) >= 5
    assert len(CYPHER_FULLTEXT_INDEXES) >= 2
