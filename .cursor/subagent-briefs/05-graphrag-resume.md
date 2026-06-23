# 05 — GraphRAG — Resume Brief (Round 2)

## Current state

You've shipped a 4-branch stack — `feat/graphrag/01-ontology-migration` → `feat/graphrag/04-mcp-evals` (tip = current `feat/graphrag/04-mcp-evals`). Nothing merged to `main` yet.

What landed across the stack:
- **01-ontology-migration**: Alembic `0002_kg_chunks.py` + ontology constraints/indexes in `services/graphrag/graphrag_service/ontology/schema.py`.
- **02-ingestion-pipeline**: real ingestion pipeline (source → chunk → embed → extract → resolve → write → verify) + seed corpus.
- **03-retrieval-modes**: local, global, hybrid, personalized; Neo4j service wired.
- **04-mcp-evals**: KG MCP server tools complete; retrieval evals wired into the CI runner.

## What's left

1. **Merge the stack to `main`** — rebase, PR per branch, `review-bugbot`, squash-merge in order. (Opus preserved any in-flight uncommitted Phase-3 cross-stream work on `wip/agents-phase3-snapshot`; do not pull from there — it's owned by stream 03/09.)
2. **Real entity resolution**: combine vector + embedding similarity + Levenshtein for concept dedup; reject if `match_score < 0.78`.
3. **Verification cycle**: nightly job that re-checks a sample of edges against fresh chunks; mark stale edges `deprecated`; surface in `MemoryHealthReport`.
4. **Personalized retrieval**: walk seeded from `(:Learner)-[:STUDIED|MASTERS]->(:Concept)` neighborhood.
5. **Reranker integration** (Cohere `rerank-3` primary, Voyage `rerank-2` fallback).
6. **End-to-end ingest of the Phase-1 course** seeded by stream 07 — Curriculum publishes lessons/objectives → GraphRAG ingests and indexes.
7. **GraphRAG MCP final polish** — ensure `kg.search`, `kg.walk`, `kg.hybrid`, `kg.ingest_document`, `kg.health` all return canonical schemas + are token-budget aware.

## Locked decisions

- Neo4j only for graph; pgvector for chunks; Postgres FTS for lexical.
- Embeddings via the shared client (Voyage primary). Same model as Memory to share cache.
- Hybrid weights default: `0.55 dense + 0.20 lexical + 0.15 KG-walk + 0.10 personalized`. Configurable via `GRAPHRAG_*` envs.
- Only `KGBuilder` and `MemorySteward` agents write to the KG (rule `40-memory-rules.mdc`).
- Ingestion idempotent by `(source_id, chunk_index, content_hash)`.

## Done when

- All 4 stack branches merged to `main`.
- Phase-1 course fully ingested into KG + pgvector on staging.
- `kg.hybrid` returns rerank-ed citations end-to-end (used by Tutor + QA + Research).
- Retrieval evals green: recall@5 ≥ baseline + 5%, MRR ≥ 0.55.
- Nightly verification job running; stale edges marked.

## Required reading

- `PLAN.md` §6, §11; `ARCHITECTURE.md` §5.
- `.cursor/rules/{20,40,60}-*.mdc`.
- `skills/graphrag-ingestion/SKILL.md`, `skills/build-an-mcp-server/SKILL.md`.
- `.cursor/subagent-briefs/05-graphrag.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the GraphRAG sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/05-graphrag-resume.md
  3. .cursor/subagent-briefs/05-graphrag.md
  4. PLAN.md §6, §11; ARCHITECTURE.md §5
  5. skills/{graphrag-ingestion,build-an-mcp-server}/SKILL.md
  6. .cursor/rules/{20,40,60}-*.mdc

Then:
  A. Walk the stack feat/graphrag/01..04 — rebase each onto current main if
     needed, open a PR per branch (conventional commit), review-bugbot, squash.
  B. Ship entity resolution upgrades (vector + embedding + Levenshtein with
     0.78 threshold).
  C. Nightly verification job (Celery beat) — mark stale edges.
  D. Personalized retrieval walk seeded by learner's neighborhood.
  E. Cohere rerank-3 (Voyage rerank-2 fallback).
  F. Coordinate with stream 07 (Curriculum) to ingest the Phase-1 course on staging.
  G. Final polish on the GraphRAG MCP server tools and retrieval eval thresholds.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. review-bugbot on every PR.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: GraphRAG is the live retrieval backbone for the deployed website,
seeded with real curriculum content.
```
