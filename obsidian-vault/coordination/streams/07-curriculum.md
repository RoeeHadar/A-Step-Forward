# Curriculum Stream (07)

Repo brief: `.cursor/subagent-briefs/07-curriculum.md`

## Vault-first docs

- [[../../curriculum/learning-path-architecture|Learning path & GraphRAG]] — how suggestions are computed
- [[../../curriculum/cross-subject-edges|Cross-subject edge authoring]]
- [[../../curriculum/kg-workflow|KG → vault workflow]]
- [[../../product/plan-and-memory|Plan & memory (product)]]

## Skills (read first)

- Repo `skills/use-obsidian-vault/SKILL.md`
- Repo `skills/use-learning-plan/SKILL.md`
- Repo `skills/cross-subject-kg/SKILL.md`
- Repo `skills/expand-lessons-cursor/SKILL.md`
- Repo `skills/author-lesson/SKILL.md`

## Scope

| Artifact | Path | Notes |
|----------|------|-------|
| KG metadata (source) | `content/knowledge-graph/*.yaml` | **156** concepts |
| Compiled KG | `apps/web/src/lib/kg-data.json` | Generated |
| Cross-subject edges | `apps/web/src/lib/kg-cross-edges.json` | ~93 curated edges |
| Path planner | `apps/web/src/lib/learning-plan.ts` | Backward BFS + mastery |
| Lessons | `scripts/seed_data/lessons/*.json` | **207** lessons |
| Concept ↔ lesson | `apps/web/src/lib/concept-aliases.ts` | Syllabus id aliases |
| Vault | `obsidian-vault/` | Primary dev KB |

## Commands

```bash
pnpm vault:build-kg      # YAML → kg-data.json
pnpm vault:sync          # KG + expansion queue → vault
node scripts/cursor-expansion-queue.mjs --next 10
```

## Vault views

- [[../../Home|Vault home]]
- [[../curriculum/learning-path-architecture|Learning path architecture]]
- [[../curriculum/kg-workflow|KG → vault workflow]]
- [[../curriculum/expansion-dashboard|Expansion dashboard]]
- [[../curriculum/expansion-queue|Expansion queue]]
- `concepts/` — one hub note per KG concept

## Open work (path planner)

- [ ] Unify `generateLearningPlan()` with `buildLearningPlan()`
- [ ] Time-horizon depth for exam cram
- [ ] Golden path defaults per `goal_key`

## Acceptance (expansion policy 2026-07-02)

- Depth + Hebrew parity per `skills/expand-lessons-cursor`
- Validate: `node scripts/audit-lesson-depth.mjs --strict --phase=4`
- Seed: `gh workflow run "Seed DB (one-shot)" -f target=lessons-from-json`
