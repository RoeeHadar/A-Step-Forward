---
type: active-context
updated: 2026-07-03
coordinator_status: .cursor/coordinator/STATUS.md
production_web: e645aa1
---

# Active Context

> Update this note at the start/end of each focused work session.

## Current focus

- **Stream**: Product alignment — learning paths, plan/memory UX, vault as primary KB
- **Status**: Frontend plan/memory fixes **shipped** (`e645aa1`); golden-path unification **not started**
- **Policy**: Obsidian vault documents architecture; repo code implements it

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

- [x] [[curriculum/learning-path-architecture|Learning path & GraphRAG architecture]]
- [x] [[curriculum/cross-subject-edges|Cross-subject edge runbook]]
- [x] [[product/plan-and-memory|Plan & memory product surface]]
- [x] [[coordination/streams/01-frontend|01-frontend stream]]
- [x] [[Home|Home]] + [[CLAUDE|CLAUDE]] — vault as primary reliance

## Next (priority order)

1. **Unify planners** — `generateLearningPlan()` should call `buildLearningPlan()` with goal + horizon
2. **Time-to-goal depth** — exam ≤7 days skips distant basics unless mastery < 0.4
3. **Golden path per `goal_key`** — curated default sequences in vault + code
4. Commit vault docs with next repo push

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
