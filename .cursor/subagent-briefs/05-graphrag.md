# 05 — GraphRAG

## Goal
Implement the knowledge graph and GraphRAG retrieval for **A Step Forward** using Neo4j (with the ontology Opus drafted), plus the ingestion pipeline (chunk → embed → extract → resolve → write), and four retrieval modes (local, global, hybrid, personalized).

## In-scope files
- `services/graphrag/**`
- `mcp-servers/graphrag/**`
- `packages/schemas/graph*.py`
- `evals/retrieval/**` (KG portion)

## Out-of-scope
- Memory service (consumes KG via events; see 04).
- Agents (consume KG via the service / MCP; see 03).

## Ontology (starting point)
Nodes: `Learner`, `Concept`, `Skill`, `Topic`, `Course`, `Lesson`, `Resource`, `Assessment`, `Question`, `Misconception`, `Goal`, `Event`, `Agent`.
Edges include: `PREREQUISITE_OF`, `TEACHES`, `COVERS`, `MASTERS{score,last_assessed_at}`, `STUDIED`, `TESTS`, `OPPOSES`, `REQUIRES`. (See `PLAN.md` §6.)

## Pipeline (must)
1. Source connectors (PDF, HTML, video transcript, lesson docs).
2. Chunk + embed (Voyage default) → pgvector.
3. Entity/relation extraction with Claude + `instructor` (typed outputs).
4. Entity resolution (link to existing nodes; fuzzy + embedding match).
5. Write to Neo4j with provenance edges to source chunks.
6. Verification pass (sample queries; flag low-confidence extractions).
7. Snapshot scheduled to object store.

## Retrieval modes
- `kg.search(query, k)` — vector local.
- `kg.walk(seed_node_ids, depth)` — graph walk.
- `kg.hybrid(query, k, depth)` — vector seed → walk → rerank.
- `kg.personalized(learner_id, query, k)` — biased toward learner subgraph.
- `kg.related_concepts(concept_id)`, `kg.prereqs(concept_id)`, `kg.next_topics(concept_id, learner_id)`, `kg.explain_path(a, b)`.

## Required reading
1. `PLAN.md` §6, §11.
2. `ARCHITECTURE.md` §1, §3.
3. `.cursor/rules/20-python-style.mdc`, `60-testing.mdc`.
4. `skills/graphrag-ingestion/SKILL.md`.

## Acceptance criteria
- Ingestion runs end-to-end on a seed corpus.
- Cypher indexes + constraints created via Alembic-style migration script.
- Retrieval evals meet `recall@10 ≥ 0.8`, `MRR ≥ 0.7` on seed test set.
- GraphRAG MCP exposes the tools listed above.
- Personalized retrieval beats non-personalized by ≥10% on the eval set.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§6, §11), ARCHITECTURE.md (§1, §3),
  .cursor/rules/20-python-style.mdc, 60-testing.mdc,
  skills/graphrag-ingestion/SKILL.md,
  .cursor/subagent-briefs/05-graphrag.md (this file).
Implement the ontology migration first, then the ingestion pipeline, then the retrieval modes, then the MCP server.
Add retrieval evals under evals/retrieval/. One PR per phase.
```
