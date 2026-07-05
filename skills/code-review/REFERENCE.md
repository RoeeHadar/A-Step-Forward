# Code Review — Reference

Checklists and false-positive filters synthesized from external skills and
ASF conventions. Load when scoring findings or auditing a module.

---

## 1. External sources (2025–2026)

| Source | Use in reviews |
|--------|----------------|
| [Addy Osmani — code-review-and-quality](https://github.com/addyosmani/agent-skills/blob/HEAD/skills/code-review-and-quality/SKILL.md) | Five axes, edge cases, presumptive blockers, test behavior |
| [Nexus — reviewing-code](https://github.com/nexus-substrate/nexus-agents/blob/main/skills/reviewing-code/SKILL.md) | Blind subagent review, 4-point verification gate, JS race rules |
| [ShipWithAI — AI PR review 2026](https://shipwithai.io/blog/reviewing-ai-generated-pull-requests-2026--part1--senior-dev--en/) | Fake tests, hallucinated imports, scope creep, hidden side effects |
| [Outfitter — code-review skill](https://playbooks.com/skills/outfitter-dev/agents/code-review) | Error-handling checklist, severity-tagged findings |
| [Troy Kelly — comprehensive-review](https://playbooks.com/skills/troykelly/claude-skills/comprehensive-review) | Edge/concurrency/state blindspots matrix |

---

## 2. Four-point verification gate (mandatory)

Before each finding:

1. **Context** — Read 5 lines before/after; full function for control flow.
2. **Observable failure** — Concrete: wrong UI value, lost row, 500 swallowed, stale SSR.
3. **Evidence** — `apps/web/src/.../file.ts:123` or range.
4. **False-positive filter** — Apply section 3 below.

No observable failure → discard finding.

---

## 3. False-positive filters (TypeScript / Next.js)

| Claim | Filter |
|-------|--------|
| Race in sync code | JS is single-threaded; need **await between read and write** or shared mutable closure across concurrent requests |
| `Map` mutation during iteration | ECMA-262 safe for `for..of` on Map |
| Intentional empty state | `[]` / zeros for brand-new learners is product policy (see `data.ts` comments) |
| `as` cast | OK if narrowed immediately with `typeof` / Zod parse |
| Missing test | NIT unless BLOCKER logic untested on hot path |
| Architecture | “Should be microservice” → escalate to stream **24**, not BLOCKER here |

---

## 4. Silent failure patterns (flag as WARN or BLOCKER)

```typescript
// BLOCKER/WARN — swallows errors
.catch(() => {})
catch { /* empty */ }

// WARN — hides misconfiguration
if (!dbConfigured) return [];

// WARN — client trust
const learnerId = body.learner_id;

// WARN — silent fallback to mock
return remote ?? MOCK_DASHBOARD;

// WARN — optional chain masking required field
profile?.subjects ?? []  // when [] causes wrong scope silently
```

**Acceptable** when paired with explicit empty-state UI copy and documented policy.

---

## 5. Reliability checklist

| Check | Question |
|-------|----------|
| Multi-step DB write | DELETE then INSERT without lock/transaction? |
| Advisory lock | Released in `finally`? |
| Idempotency | Retry-safe POST handlers? |
| Cron overlap | Same job on Vercel + GHA? |
| SSR cache | Learner page missing `force-dynamic`? |
| Parallel `Promise.all` | Partial failure handling? |
| LLM parse failure | Returns `{ ran: false, reason }` not fake success? |

---

## 6. Correctness & edge cases

| Input / state | Ask |
|---------------|-----|
| `null` profile | Onboarding redirect? 503? |
| Empty mastery | Division by zero in averages? |
| Missing `DATABASE_URL` | 503 JSON, not crash? |
| Invalid UUID / concept id | 400 not 500? |
| Hebrew locale | User-facing strings from i18n? |
| Clerk unauthenticated | 401 on API routes? |
| Plan missing | Dashboard empty state, not throw? |

---

## 7. Clarity & over-engineering

**Flag WARN when:**

- Function > ~80 lines with multiple responsibilities (suggest split at natural boundary).
- Helper used once and adds indirection.
- Generic `utils.ts` growth without domain name.
- Comments restate obvious code.
- Duplicate logic vs existing `neon-db` / `concept-scope` helper.

**Prefer:** match surrounding file style; smallest fix that preserves behavior.

---

## 8. Test quality

| Good | Bad |
|------|-----|
| Asserts return value / DB state | `expect(true).toBe(true)` |
| Tests behavior contract | Tests private implementation |
| Edge case named in test title | Only happy path |
| Pure logic unit tests | Network in unit tests without mock |

Integration tests in `apps/web/src/lib/*.integration.test.ts` require Neon — note when skipped locally.

---

## 9. ASF hotspot files (extra scrutiny)

| Area | Paths | Common issues |
|------|-------|---------------|
| Neon access | `neon-db.ts`, `persona-consolidator.ts` | God module, races, silent catch |
| Chat | `app/api/chat/route.ts` | Context size, scope filters, stream errors |
| Plan | `plan-apply.ts`, `generateLearningPlan`, `learning-plan.ts` | Dual planner drift, lock usage |
| Auth | `lib/auth.ts`, API routes | learner_id trust |
| Legacy API | `lib/data.ts`, `/api/dashboard`, `/api/memory` | Render proxy |
| i18n | `i18n/messages.ts`, landing/dashboard components | Hardcoded English |
| Cron | `api/cron/*`, `vercel.json` | Duplicate schedules, missing CRON_SECRET |

---

## 10. Escalation matrix

| Finding type | Escalate to |
|--------------|-------------|
| RBAC, secrets, injection, CSP | Stream **10** + `review-security` |
| Service split, ADR, planner authority | Stream **24** |
| Prompt regression, eval threshold | Stream **08** |
| Infra, cron, deploy | Stream **09** |
| Curriculum / planner product rules | Stream **07** |

---

## 11. Verdict rubric

| Verdict | Condition |
|---------|-----------|
| **SHIP** | Zero BLOCKER; WARNs documented and acceptable |
| **SHIP WITH WARNINGS** | Zero BLOCKER; WARNs tracked for immediate follow-up |
| **DO NOT SHIP** | Any unresolved BLOCKER |

---

## 12. Diff review commands (reviewer use)

```powershell
git diff main...HEAD --stat
git diff main...HEAD -- apps/web/src/path/to/file.ts
pnpm --filter @asf/web lint
pnpm --filter @asf/web exec tsc --noEmit
pnpm --filter @asf/web exec vitest run path/to/test.ts
```

Run what applies; cite command output in report for BLOCKERs when possible.
