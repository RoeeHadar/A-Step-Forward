---
type: active-context
updated: 2026-07-11
coordinator_status: .cursor/coordinator/STATUS.md
production_web: ff021ca9
---

# Active Context

> Update this note at the start/end of each focused work session.
> Machine-readable session trail: `docs/reviews/LAST_DONE.md` + `MEMORY_SNAPSHOT.md` (`<!-- LAST_SESSION -->`).

## Last done (2026-07-11)

- [x] **Unified planner (ADR-0007 / PR1)** — `generateLearningPlan()` delegates to `buildUnifiedPlanConceptOrder()` → `buildLearningPlan()` via `plan-worklist.ts`
- [x] **Wellbeing module (ADR-0008 / PR2–PR3)** — `wellbeing-plan-bias.ts`, morale blending, cooldown gates, anxiety intent snapshot injection, dashboard plan-adjustment notice
- [x] **Chat context compaction (PR3)** — compact baseline, 4-turn session-gated memory, direct Groq hot path
- [x] **ADR-0008 accepted** — doc reconciliation (PR4) updates ADRs, skills, vault

## Current focus

- **Stream**: Content gaps — authored lesson coverage, golden-path depth per `goal_key`
- **Status**: Planner unification + wellbeing overlay **shipped** on `feat/frontend/unify-planners-pr1`; pilot has no active learners yet
- **Policy**: Obsidian vault documents architecture; repo code implements it
- **Trail file**: [[../docs/reviews/LAST_DONE|LAST_DONE]] (repo path `docs/reviews/LAST_DONE.md`)

## Shipped (2026-07-03)

### Frontend (`e645aa1`)

- [x] Memory tab — read-only snapshot (profile, persona, plan focus, scoped mastery, agent notes)
- [x] Template-only plan apply — sidebar **עדכון תוכנית לימוד** alone
- [x] `concept-scope.ts` — plan-scoped weak/strong; lesson-index subject resolution
- [x] Tutor redirect on casual plan-change requests (baseline + turn injection)
- [x] Weekly quiz locale + plan-week concepts

### Curriculum / KG (earlier 2026-07-03)

- [x] KG enrichment — **156/156** concepts, all ≥5 skill atoms, all `level_scope` filled
- [x] Vault — **156** notes, all `data_completeness: full`
- [x] Lessons — **207/207** marked done in expansion queue
- [x] MCP **`asf-obsidian`** connected

## Vault updates (this session)

- [x] [[curriculum/learning-path-architecture|Learning path & GraphRAG architecture]] — unified planner + wellbeing module
- [x] ADR index — 0007 via 0008, 0008 accepted
- [x] Skills — `chat-memory-context`, `use-learning-plan`

## Next (priority order)

1. **Content gaps** — `hasLesson: false` concepts on golden paths; expand authored lessons for Bagrut 372/471/572 tracks
2. **Time-to-goal depth** — exam ≤7 days skips distant basics unless mastery < 0.4 (partial; verify integration tests)
3. **Golden path per `goal_key`** — curated default sequences in vault + code
4. **Integration tests** — `plan-neon.integration.test.ts`, wellbeing cooldown matrix
5. Commit vault docs with next repo push

## KG pipeline

```
content/knowledge-graph/*.yaml
        ↓  pnpm vault:build-kg
apps/web/src/lib/kg-data.json
        +
apps/web/src/lib/kg-cross-edges.json  →  learning-plan.ts (backward walk)
        ↓  pnpm vault:sync-concepts
obsidian-vault/concepts/*.md
```

## Links

- [[Home|Vault home]]
- [[curriculum/learning-path-architecture|Learning paths]]
- [[product/plan-and-memory|Plan & memory]]
- [[curriculum/kg-workflow|KG → vault workflow]]
- [[curriculum/expansion-dashboard|Expansion dashboard]]
- [[coordination/streams/01-frontend|Frontend stream]]
