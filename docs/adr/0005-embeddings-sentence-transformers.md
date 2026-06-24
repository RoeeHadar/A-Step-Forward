# ADR-0005 — Sentence-Transformers for GraphRAG embeddings

- **Status**: Accepted
- **Date**: 2026-06-24
- **Deciders**: Opus + GraphRAG sub-agent (Composer 2.5)

## Context

GraphRAG stores chunk embeddings in Postgres (`kg_chunks.embedding` via pgvector)
for dense retrieval and seeds Neo4j with Concept/Lesson nodes extracted from
curriculum markdown. The original brief defaulted to Voyage `voyage-3-large`
(1024-dim), which is a paid API and conflicts with the project owner's
**no paid providers** constraint (see ADR-0004).

Phase-1 launch requires ingesting the `foundations-of-math` course (9 lesson
files, ≥30 chunks) into Neon + Neo4j AuraDB Free without incurring embedding
API costs.

## Decision

Adopt **HuggingFace `sentence-transformers/all-MiniLM-L6-v2`** as the GraphRAG
embedding model:

- **Dimensions**: 384 (requires Alembic migration `0006_kg_chunks_384` to alter
  `kg_chunks.embedding` from `vector(1024)` to `vector(384)`).
- **Runtime**: local inference via the `sentence-transformers` Python package;
  loaded once per process, encoded in a thread pool for async compatibility.
- **Fallback chain**: sentence-transformers → deterministic hash embedding (CI /
  missing deps) → Voyage API only when explicitly configured with
  `GRAPHRAG_EMBEDDING_MODEL=voyage-3-large` and `VOYAGE_API_KEY`.
- **Settings defaults** (`GraphRAGSettings`):
  - `embedding_model = "sentence-transformers/all-MiniLM-L6-v2"`
  - `embedding_dim = 384`

## Consequences

### Positive

- Zero marginal cost for embedding at ingest and query time.
- Works offline in dev/CI without API keys.
- Model is small (~80 MB), fast on CPU, widely benchmarked for semantic search.

### Negative

- Lower retrieval quality vs. Voyage/Cohere on long educational passages; may
  need reranker tuning or model upgrade post-launch.
- Adds `sentence-transformers` (+ PyTorch) as a GraphRAG dependency — increases
  install size and cold-start time for ingestion workers.
- Embedding dimension differs from Memory service (if Memory later adopts a
  different model, cross-service embedding cache sharing is not possible
  without alignment).

### Follow-ups

- Re-evaluate with retrieval evals (`evals/retrieval/`) once a free reranker
  path is chosen (ADR pending).
- Consider `all-mpnet-base-v2` (768d) if eval recall@5 falls below baseline.

## Alternatives considered

| Option | Why rejected |
| --- | --- |
| Voyage `voyage-3-large` | Paid API; violates no-paid-providers constraint |
| OpenAI `text-embedding-3-small` | Paid API |
| Cohere embed | Paid API |
| `all-mpnet-base-v2` (768d) | Better quality but larger; 384d chosen for Aura/Neon free-tier footprint |
| Deterministic hash only | No semantic similarity — unusable for hybrid retrieval |
