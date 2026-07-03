---
type: product
tags:
  - product/learning-plan
  - product/memory
  - frontend
updated: 2026-07-03
---

# Plan & Memory (Product Surface)

Runtime behavior on Vercel + Neon. Vault documents **what shipped** and **rules agents must follow**.

## Learning plan update (Tutor only)

| Rule | Implementation |
|------|----------------|
| Apply only via official template | `plan-change-template.ts` → `isPlanChangeTemplate()` |
| Template must be **alone** in message | No casual text + template in same turn |
| UI panel | `plan-change-template-panel.tsx` — Tutor chat sidebar only |
| Server apply | `plan-apply.ts` → `executePlanUpdate()` → `generateLearningPlan()` |
| Success UI | `agent-chat.tsx` — ✅ only from `plan_updated` data event, not LLM text |

**Agent behavior (non-negotiable):**

- Baseline: `apps/web/src/lib/agent-baseline.ts` — universal learning-plan rule
- Tutor/Mentor: `PLAN_AGENT_INSTRUCTIONS` + `CASUAL_PLAN_CHANGE_TURN_INSTRUCTION` on heuristic casual requests
- Casual “change my plan” → redirect to sidebar **עדכון תוכנית לימוד**; no exam-scope Q&A substitute

## Memory tab (`/app/memory`)

Read-only aggregate: `getLearnerMemorySnapshot()` in `neon-db.ts`.

| Section | Source |
|---------|--------|
| Onboarding profile | `learner_profiles` |
| Shared persona | `learner_profiles.learner_persona` |
| Plan focus | `learning_plans` + `plan_weeks` (active week concepts) |
| Weak / strong signals | `concept_mastery` filtered by [[../curriculum/learning-path-architecture#Concept scoping (2026-07-03)|concept-scope]] |
| Agent notes | `learner_agent_notes` per agent |

Learners **do not edit memory directly** — chat with Tutor/Mentor to change persona/plan.

## Mastery scoping (2026-07-03)

`apps/web/src/lib/concept-scope.ts`

- When a plan exists: weak/strong limited to **plan week concepts**
- Resolves lesson ids (e.g. `sequences_5pt`) via `lessons-index.generated.json`
- Physics profile must not show unrelated math weak areas

## Weekly quiz

- Route: `/quiz/[week_id]`
- Concepts from **active plan week**, locale from cookie
- Grading: server-side via lesson answer routes

## Commits (reference)

| SHA | Summary |
|-----|---------|
| `6f015db` | Memory tab rebuild, quiz/plan alignment |
| `e6f0959` | Strict template-only apply |
| `870534d` | Subject-scoped memory signals |
| `e645aa1` | Plan-scoped mastery + template redirect enforcement |

## Related

- [[../curriculum/learning-path-architecture|Learning path architecture]]
- [[../coordination/streams/01-frontend|Frontend stream]]
- Repo: `skills/use-learning-plan/SKILL.md`, `skills/chat-memory-context/SKILL.md`
