---
type: coordination
stream: "01-frontend"
updated: 2026-07-03
---

# Frontend Stream (01)

Repo brief: `.cursor/subagent-briefs/01-frontend.md`

## Vault-first docs (read before coding)

- [[../../product/plan-and-memory|Plan & memory product surface]]
- [[../../curriculum/learning-path-architecture|Learning path & GraphRAG]]
- [[../../Home|Vault home]] · [[../../_active-context|Active context]]

## Recent shipped (2026-07-03)

| Area | Key files |
|------|-----------|
| Memory tab (read-only) | `memory-overview.tsx`, `getLearnerMemorySnapshot()` |
| Template-only plan apply | `plan-change-template.ts`, `plan-apply.ts` |
| Plan-scoped mastery | `concept-scope.ts`, `neon-db.ts`, `chat/route.ts` |
| Tutor template redirect | `agent-baseline.ts`, `plan-actions.ts` |
| Weekly quiz | `weekly-quiz.ts`, `week-quiz-client.tsx` |

Production HEAD (2026-07-03): `e645aa1`.

## Open work

- [ ] Unify weekly plan generator with `buildLearningPlan()` ([[../../curriculum/learning-path-architecture#Known gaps (2026-07-03)|gaps]])
- [ ] Time-horizon depth trimming in path planner
- [ ] Golden path per `goal_key` defaults

## Commands

```bash
pnpm --filter @asf/web lint
pnpm --filter @asf/web build
pnpm --filter @asf/web exec vitest run src/lib/concept-scope.test.ts
```

## Related

- [[07-curriculum|Curriculum stream]] — KG + lessons feed the planner
- Repo: `.cursor/skills/add-a-frontend-page/SKILL.md`, `.cursor/skills/neon-direct-route/SKILL.md`
