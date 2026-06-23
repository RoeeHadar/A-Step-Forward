---
name: graphrag-ingestion
description: How to ingest content into the Knowledge Graph + pgvector, run entity/relation extraction, resolve entities, and verify. Read BEFORE modifying GraphRAG ingestion code.
---

# GraphRAG Ingestion

## Ontology
See `PLAN.md` §6. Treat the ontology as a contract; new node/edge types require an ADR.

## Pipeline (`services/graphrag/graphrag_service/ingest/`)
1. **Source** — connectors for PDF, HTML, Markdown, transcripts. Each connector produces `RawDocument`.
2. **Chunk** — semantic chunking (200–800 tokens, overlap 50). Preserve headings + ordinal.
3. **Embed** — Voyage `voyage-3-large` by default; insert into pgvector `kg_chunks`.
4. **Extract** — Claude w/ `instructor` returns:
   ```
   class Extraction(BaseModel):
       entities: list[Entity]
       relations: list[Relation]
       claims: list[Claim]            # for verification later
       confidence: float
   ```
5. **Resolve** — for each entity: fuzzy match name + embedding match against existing nodes. If `score ≥ τ_link`, link; else create with `pending_review=true`.
6. **Write to Neo4j** — MERGE nodes, MERGE edges with `provenance` (chunk_id, model, ts).
7. **Verify** — sample `m` claims per batch; run a small QA prompt against the graph; flag mismatches.
8. **Snapshot** — periodic graph snapshot to object storage.

## Retrieval modes
- `kg.search(query, k)` — vector local.
- `kg.walk(seed_ids, depth)` — BFS with edge-type filter.
- `kg.hybrid(query, k, depth)` — vector seed → walk → rerank (Cohere/Voyage).
- `kg.personalized(learner_id, query, k)` — bias toward subgraph touching `Learner` node.
- Helpers: `kg.related_concepts`, `kg.prereqs`, `kg.next_topics`, `kg.explain_path`.

## Constraints / indexes (Neo4j)
- Unique on `Concept(canonical_name)`, `Lesson(id)`, `Learner(id)`.
- Vector index on `Chunk.embedding` if storing chunks in Neo4j; otherwise rely on pgvector.

## Pitfalls
- Don't ingest without dedupe — re-running should be idempotent (MERGE everywhere).
- Don't write low-confidence extractions silently — set `pending_review` and surface in admin.
- Don't bypass the provenance edge — every claim must be traceable to a chunk.
- Don't put PII into the KG. If a learner is the entity, prefer pseudonymous IDs.
