# 04 — Memory Service

## Goal
Productionize the memory system whose foundation Opus laid in `services/memory/`. Implement the eight memory types, hybrid retrieval, importance scoring, dreaming, consolidation, decay, conflict resolution, hierarchical summaries, context-window compaction, verification cycle, and the Memory Inspector APIs.

## In-scope files
- `services/memory/**`
- `mcp-servers/memory/**`
- `infra/alembic/versions/**` (memory tables only)
- `packages/schemas/memory*.py`
- `evals/memory/**`

## Out-of-scope
- GraphRAG (consumes memory writes via events; see 05).
- Agents (consume memory via the service / MCP; see 03).

## Key components to ship
1. **Stores** — Postgres tables, pgvector indexes, repository classes per memory type.
2. **Hygiene**:
   - `pii.py` — Presidio + custom rule pre-write redaction.
   - `importance.py` — heuristic + LLM-judge scoring.
   - `consolidation.py` — near-duplicate merge with conflict resolution.
   - `decay.py` — Ebbinghaus-style decay + access reinforcement.
   - `selective_forgetting.py` — archival sweep.
   - `compression.py` — hierarchical summaries (daily/weekly/monthly).
   - `compaction.py` — context-window compaction utility for the orchestrator.
   - `conflict_resolution.py` — `superseded_by` versioning.
   - `verification.py` — periodic re-validation prompts.
3. **Retrieval** — hybrid BM25 + dense + KG-walk + rerank, with policy filter.
4. **Dreaming** — async pipeline triggered by `MemorySteward` agent + Celery beat (`memory.dream_learner`).
5. **APIs** — REST endpoints + MCP server.
6. **Memory Inspector** — endpoints behind learner auth: list, search, view provenance, edit, delete (hard-delete cascades to embeddings + KG).
7. **Audit** — `audit_memory_events` table writes on every read/write.

## Required reading
1. `PLAN.md` §5 (entire), §10, §11.
2. `ARCHITECTURE.md` §3, §4.
3. `.cursor/rules/20-python-style.mdc`, `40-memory-rules.mdc`, `50-security.mdc`, `60-testing.mdc`.
4. `skills/memory-operations/SKILL.md`, `skills/dreaming-and-consolidation/SKILL.md`, `skills/db-migrations/SKILL.md`.

## Acceptance criteria
- All eight memory types persisted + retrievable.
- Hybrid retrieval recall@10 ≥ 0.85 on `evals/memory/retrieval/*.yaml`.
- Dreaming job runs on cron + on demand; emits MemoryHealth report.
- Consolidation merges near-duplicates without losing provenance.
- Decay sweep archives below-threshold memories (not deletes).
- Conflict resolution never silently overwrites; eval test covers contradictions.
- Context compaction keeps last K turns verbatim + structured summary block.
- PII redaction tests pass (no PII leaks in stored content).
- Delete-on-request cascades to pgvector and KG.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§5, §10, §11), ARCHITECTURE.md (§3, §4),
  .cursor/rules/20-python-style.mdc, 40-memory-rules.mdc, 50-security.mdc, 60-testing.mdc,
  skills/memory-operations/SKILL.md, skills/dreaming-and-consolidation/SKILL.md, skills/db-migrations/SKILL.md,
  .cursor/subagent-briefs/04-memory.md (this file).
Then implement the components in order: stores → hygiene → retrieval → dreaming → APIs → Inspector.
One PR per component. Add evals under evals/memory/ for every behavior.
```
