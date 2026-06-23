"""Neo4j schema (constraints + indexes) for the KG ontology.

Apply via `services/graphrag/scripts/apply_schema.py` (added by sub-agent 05).
"""

from __future__ import annotations

CYPHER_CONSTRAINTS: list[str] = [
    "CREATE CONSTRAINT learner_id IF NOT EXISTS FOR (n:Learner) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT concept_canonical IF NOT EXISTS FOR (n:Concept) REQUIRE n.canonical_name IS UNIQUE",
    "CREATE CONSTRAINT skill_canonical IF NOT EXISTS FOR (n:Skill) REQUIRE n.canonical_name IS UNIQUE",
    "CREATE CONSTRAINT topic_canonical IF NOT EXISTS FOR (n:Topic) REQUIRE n.canonical_name IS UNIQUE",
    "CREATE CONSTRAINT course_id IF NOT EXISTS FOR (n:Course) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT lesson_id IF NOT EXISTS FOR (n:Lesson) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (n:Resource) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT assessment_id IF NOT EXISTS FOR (n:Assessment) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (n:Question) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT misconception_id IF NOT EXISTS FOR (n:Misconception) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT goal_id IF NOT EXISTS FOR (n:Goal) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT agent_name IF NOT EXISTS FOR (n:Agent) REQUIRE n.name IS UNIQUE",
]

CYPHER_INDEXES: list[str] = [
    "CREATE INDEX concept_aliases IF NOT EXISTS FOR (n:Concept) ON (n.aliases)",
    "CREATE INDEX concept_pending IF NOT EXISTS FOR (n:Concept) ON (n.pending_review)",
    "CREATE INDEX lesson_title IF NOT EXISTS FOR (n:Lesson) ON (n.title)",
    "CREATE INDEX resource_title IF NOT EXISTS FOR (n:Resource) ON (n.title)",
    "CREATE INDEX node_canonical_name IF NOT EXISTS FOR (n) ON (n.canonical_name)",
    "CREATE INDEX masters_score IF NOT EXISTS FOR ()-[r:MASTERS]-() ON (r.score)",
    "CREATE INDEX prereq_weight IF NOT EXISTS FOR ()-[r:PREREQUISITE_OF]-() ON (r.weight)",
    "CREATE INDEX derived_from_chunk IF NOT EXISTS FOR ()-[r:DERIVED_FROM]-() ON (r.chunk_id)",
]

# Full-text indexes for local (non-vector) fallback search.
CYPHER_FULLTEXT_INDEXES: list[str] = [
    (
        "CREATE FULLTEXT INDEX concept_search IF NOT EXISTS "
        "FOR (n:Concept) ON EACH [n.canonical_name, n.summary]"
    ),
    (
        "CREATE FULLTEXT INDEX resource_search IF NOT EXISTS "
        "FOR (n:Resource) ON EACH [n.canonical_name, n.summary, n.title]"
    ),
]
