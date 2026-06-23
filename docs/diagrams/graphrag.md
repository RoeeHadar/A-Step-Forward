# GraphRAG — data flow

Hybrid retrieval over a per-learner knowledge graph. Ingestion is a deterministic
pipeline; retrieval is a routed mix of BM25, dense, and graph traversal,
followed by a Cohere/Voyage rerank.

## Ingestion

```mermaid
flowchart LR
    subgraph Sources
      MD[markdown lessons]
      HTML[web pages]
      PDF[PDFs]
      XSCR[video transcripts]
    end

    MD --> CHUNK[chunker]
    HTML --> CHUNK
    PDF --> CHUNK
    XSCR --> CHUNK

    CHUNK --> EMB[embedder<br/>Voyage]
    CHUNK --> EXT[entity / relation extractor]

    EXT --> RES[entity resolver<br/>dedup + alias]
    RES --> SNAP[ontology snapshot]

    EMB --> CHUNKS[(chunk_repository<br/>pgvector)]
    SNAP --> NEO[(neo4j_store<br/>nodes + edges)]
    CHUNKS --> VERIF[verifier]
    NEO --> VERIF
    VERIF --> WRITE[writer<br/>commits atomic batch]
```

## Retrieval (`kg.hybrid`)

```mermaid
flowchart LR
    Q[query]
    Q --> R[router]
    R -->|keyword| BM25[BM25 over chunks]
    R -->|semantic| DENSE[dense kNN<br/>pgvector]
    R -->|relational| GRAPH[Neo4j traversal<br/>kg_chunks edges]
    BM25 --> MERGE[fusion]
    DENSE --> MERGE
    GRAPH --> MERGE
    MERGE --> RERANK[Cohere/Voyage rerank]
    RERANK --> CITE[cited answer payload]
```

## Stores

- `chunks`: Postgres + pgvector (per-learner, scoped by `learner_id`).
- `kg_chunks`: link table between Neo4j entities and chunk IDs
  (`infra/alembic/versions/0002_kg_chunks.py`).
- Neo4j: AuraDB Free in prod; `neo4j` Compose service locally.
- Ontology snapshots are versioned in `infra/alembic/versions/`.

## SLO targets (Phase-1)

- p50 ingestion: ≤ 5s / 5k tokens.
- p95 retrieval (warm cache): ≤ 350ms.
- Recall@10 (math seed corpus): ≥ 0.85.
- Precision@10 (math seed corpus): ≥ 0.65.

Live thresholds live in `evals/retrieval/kg/thresholds.yaml`.
