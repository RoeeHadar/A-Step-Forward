# 04 — Memory Service — Resume Brief (Round 2)

## Current state

Phase 0/1 (on `main`):
- Schemas in `packages/schemas/schemas/memory.py` (8 types, records, search, health).
- Service: `services/memory/memory_service/{api.py,default_service.py,settings.py}`.
- Stores: in-memory repository scaffold (`stores/repository.py`).
- Hygiene: PII, importance, decay, consolidation, conflict resolution, selective forgetting, compression, compaction, verification, dreaming, audit — all present as functioning Phase-0 implementations.
- Retrieval: hybrid (lexical + recency + confidence) + policy filter.
- Phase-0 smoke test green: `services/memory/tests/test_smoke.py`.
- Alembic migration `infra/alembic/versions/0002_memory_tables.py` exists.

## What's left (Phase 2 — real implementation)

1. **Swap in Postgres + pgvector** (replace in-memory repository with SQLAlchemy 2.0 async + pgvector). Honor the existing API surface so feature code doesn't change.
2. **Real embeddings**: Voyage `voyage-3-large` via the shared LLM/embedding client; cache embeddings; backfill task for missing embeddings.
3. **Real PII**: swap `hygiene/pii.py` for Presidio + custom recognizers (en + he starter).
4. **Real importance scoring**: heuristic + a cheap-model LLM judge with `instructor`-validated output; LRU-cache by content hash.
5. **Hybrid retrieval upgrade**: BM25 (Postgres FTS) + dense (pgvector) + KG-walk seeded via GraphRAG MCP + Cohere/Voyage rerank.
6. **Dreaming worker**: implement the full pipeline in `hygiene/dreaming.py` (currently stages but no LLM-driven pattern extraction). Wire to Celery beat (already scheduled).
7. **Consolidation + conflict resolution**: real LLM-judge contradiction detection; merge that preserves provenance + sums access counts; never silent-overwrite.
8. **Memory Health report** persisted; exposed via `GET /v1/memory/health` (coordinate with stream 02).
9. **Memory Inspector** backend support: timeline, search, edit-with-reason, delete-with-cascade (cascades to pgvector and KG via GraphRAG MCP).
10. **Audit table** (Postgres-backed) + read-only admin endpoint.
11. **Coverage ≥ 80%** including evals under `evals/memory/{dreaming,consolidation,decay,conflict,pii}/`.

## Locked decisions

- Embeddings: Voyage `voyage-3-large` (1024-d). Fallback: OpenAI `text-embedding-3-large`.
- Rerank: Cohere `rerank-3` (fallback Voyage `rerank-2`).
- Decay τ default: 14 days; reinforced by access.
- Consolidation cosine threshold: 0.92 (configurable).
- Memory writes are *never* awaited inline on hot read paths beyond the immediate event — always batch / queue heavier processing.

## Done when

- All Phase-2 items above shipped.
- Memory tables migrated and indexed in CI + staging Postgres.
- Dreamer runs nightly and produces a `MemoryHealthReport`.
- Inspector endpoints return real data; deletes cascade.
- Evals green: `evals/memory/*` thresholds met.

## Required reading

- `PLAN.md` §5 (entire), §10, §11; `ARCHITECTURE.md` §3–4.
- `.cursor/rules/{20,40,50,60}-*.mdc`.
- `skills/{memory-operations,dreaming-and-consolidation,db-migrations}/SKILL.md`.
- `.cursor/subagent-briefs/04-memory.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Memory sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/04-memory-resume.md
  3. .cursor/subagent-briefs/04-memory.md
  4. PLAN.md §5, §10, §11; ARCHITECTURE.md §3–4
  5. skills/{memory-operations,dreaming-and-consolidation,db-migrations}/SKILL.md
  6. .cursor/rules/{20,40,50,60}-*.mdc

Then implement in this order, one PR per step:
  1. SQLAlchemy 2.0 async + pgvector repository (replaces in-memory store)
  2. Voyage embeddings + cache + backfill task
  3. Presidio-based PII redaction (en + he starter)
  4. Importance scoring with cheap-model LLM judge (instructor-validated)
  5. Hybrid retrieval upgrade (BM25 + dense + KG-walk + rerank)
  6. Dreaming pipeline LLM-driven; Celery wired
  7. Conflict resolution with LLM judge; merges preserving provenance
  8. MemoryHealthReport persistence + GET /v1/memory/health (coord stream 02)
  9. Memory Inspector endpoints — timeline / edit-with-reason / delete-cascade
  10. Postgres-backed audit table + admin endpoint
  11. evals/memory/{dreaming,consolidation,decay,conflict,pii}/ with green thresholds

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. review-bugbot every PR. review-security on PII/auth/RBAC.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: memory is real, persistent, observed, healthy, and ready for the
deployed app to rely on through the upcoming launch.
```
