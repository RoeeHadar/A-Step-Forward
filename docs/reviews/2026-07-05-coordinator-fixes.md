# Code Review: Coordinator architecture fixes

- **Date:** 2026-07-05
- **Reviewer:** Code Reviewer (Cursor sub-agent)
- **Scope:** Uncommitted coordinator fixes — `neon-db.ts` (locks + mapper), `/api/dashboard`, `/api/memory`, `persona-consolidator.ts`, GHA cron backstop, `memory-steward-consolidate` skill
- **Intent:** Migrate legacy dashboard/memory API routes to Neon-direct; add per-learner advisory locks for plan generation and consolidation; dedupe weekly consolidation cron (Vercel-only schedule)
- **Verdict:** **SHIP WITH WARNINGS** (original review)
- **Remediation (2026-07-07):** R1–R5 + keep-warm CI noise landed in `362f813b` / `ff021ca9` — see `docs/reviews/LAST_DONE.md`

---

## Summary

The change set is directionally correct: auth boundaries are preserved (`learnerId` from Clerk context), legacy Render proxies are removed from two hot read routes, and consolidation cron duplication is fixed. Lint and typecheck pass. The main risks are **(1)** session advisory locks on the Neon HTTP driver may not serialize concurrent writes across Vercel instances, **(2)** plan regeneration remains a non-transactional DELETE-then-INSERT sequence, and **(3)** several paths still return empty payloads instead of explicit 503/errors when the DB misbehaves. No BLOCKERs found for merge; WARNs should be tracked immediately after ship.

---

## Scope reviewed

| Path / area | Notes |
|-------------|-------|
| `apps/web/src/lib/neon-db.ts` | `tryLearnerAdvisoryLock`, `releaseLearnerAdvisoryLock`, lock in `generateLearningPlan`, `mapDashboardSnapshotToLearnerDashboard` |
| `apps/web/src/app/api/dashboard/route.ts` | Neon-direct GET |
| `apps/web/src/app/api/memory/route.ts` | Neon-direct GET |
| `apps/web/src/lib/persona-consolidator.ts` | Consolidation lock + `finally` release |
| `.github/workflows/cron-consolidate-memory.yml` | Schedule removed; manual backstop only |
| `.cursor/skills/memory-steward-consolidate/SKILL.md` | Docs aligned with single cron owner |

### Out of scope

- ADR drafts (`docs/adr/0006`, `0007`), architecture assessment prose, obsidian vault edits, stream 24/25 skill scaffolding (not runtime code).

### Commands run

- [x] `pnpm --filter @asf/web lint` — pass
- [x] `pnpm --filter @asf/web exec tsc --noEmit` — pass
- [ ] `vitest` — not run for lock/mapper (no unit tests exist yet; integration tests require Neon)
- [ ] Other: full diff reviewed via `git diff`

---

## Findings

| ID | Sev | Location | Issue | Observable failure | Fix hint |
|----|-----|----------|-------|-------------------|----------|
| R1 | WARN | `neon-db.ts:41-55`, `637-694`, `persona-consolidator.ts:188-231` | Session `pg_try_advisory_lock` on Neon HTTP driver without `sql.transaction()` | Two concurrent plan regens or consolidations for the same learner on **different** Vercel instances can both proceed; lock may not span separate HTTP round-trips | Wrap lock + writes in `neon` transaction callback, or use row-level lock / `FOR UPDATE` on a dedicated lock table; see Neon serverless transaction docs |
| R2 | WARN | `neon-db.ts:643-695` | Plan persist is DELETE → INSERT with no transaction | Mid-loop failure after DELETE leaves learner with **no plan** until retry | Single transaction or upsert pattern; rollback on failure |
| R3 | WARN | `dashboard/route.ts:20-22`, `memory/route.ts:16-18` | `dbConfigured === false` returns empty 200 JSON | Misconfigured prod (`DATABASE_URL` missing) shows “no data” UI instead of 503 — ops harder to detect | Match `plans/generate/route.ts`: return `{ error: '...' }` with 503 |
| R4 | WARN | `neon-db.ts:2445-2449`, `2928-2932` | DB errors swallowed → empty snapshot / `[]` in production (no log) | Transient Neon outage looks like empty dashboard/memory for learners; no alert trail | Log at `warn` in prod; optionally 503 from API routes when snapshot helper signals failure |
| R5 | WARN | — | No unit tests for locks, mapper, or route wiring | Regressions in lock scope or JSON shape won't be caught in CI | Add pure tests for `mapDashboardSnapshotToLearnerDashboard`; mock-sql tests for lock acquire/release contract |
| R6 | NIT | `data.ts:64-124` | `fetchDashboard` / `fetchMemories` now unused | Dead exports; future reader may call Render path by mistake | Remove or mark `@deprecated` with pointer to neon routes |
| R7 | NIT | `neon-db.ts:51-54` | `releaseLearnerAdvisoryLock` ignores `pg_advisory_unlock` result | Rare: unlock on wrong session silently no-ops | Check return value in dev; document session coupling |

### Detail (BLOCKER and WARN)

#### R1 — Advisory locks may not serialize cross-instance writes

**Location:** `apps/web/src/lib/neon-db.ts:41-55`, `637-694`; `apps/web/src/lib/persona-consolidator.ts:188-231`

**Issue:** Module header states HTTP serverless (`@neondatabase/serverless`, no TCP pool). PostgreSQL advisory locks are **session-scoped**. Lock acquire, DELETE/INSERT, and unlock are separate `sql` tagged-template calls — not wrapped in `sql.transaction()`. Concurrent invocations on different serverless instances use different DB sessions, so both can acquire `pg_try_advisory_lock(hashtext(...))` successfully.

**Failure scenario:** Learner triggers plan apply from chat while `/api/plans/generate` runs; both DELETE existing plans and INSERT overlapping rows — partial weeks, lost plan, or duplicate active plans.

**Suggested fix:** Use Neon's interactive transaction API so lock + all writes share one session; or replace with explicit `learner_plan_locks` row + `SELECT … FOR UPDATE`.

**Owner stream:** 02-backend-api (+ escalate 24-architecture for ADR on locking strategy)

#### R2 — Non-transactional plan replacement

**Location:** `apps/web/src/lib/neon-db.ts:643-695`

**Issue:** `DELETE FROM plan_weeks` / `DELETE FROM learning_plans` run before all `INSERT`s complete. Any thrown error after DELETE (network, constraint, timeout) leaves the learner without a plan.

**Failure scenario:** Week 3 INSERT fails → learner sees empty plan on dashboard until manual regen.

**Suggested fix:** Wrap entire persist block in one transaction; consider soft-delete or versioned plans for safer rollback.

**Owner stream:** 02-backend-api / 07-curriculum (planner)

#### R3 — Misconfiguration returns empty success

**Location:** `apps/web/src/app/api/dashboard/route.ts:20-22`; `apps/web/src/app/api/memory/route.ts:16-18`

**Issue:** When `dbConfigured` is false, routes return `200` with empty arrays/objects. Contrast with `apps/web/src/app/api/plans/generate/route.ts:10-12` which returns `503`.

**Failure scenario:** Deploy without `DATABASE_URL` → client hooks/pages show “no activity yet” forever; no obvious server error.

**Suggested fix:** Return `503` + `{ error: 'DATABASE_URL not configured' }` for consistency.

**Owner stream:** 02-backend-api

#### R4 — Silent empty fallback on DB errors (production)

**Location:** `apps/web/src/lib/neon-db.ts:2445-2449`, `2928-2932`

**Issue:** `getDashboardSnapshot` and `getMemoryTimelineFromNeon` catch all errors and return empty structures; logging only when `NODE_ENV !== 'production'`.

**Failure scenario:** Brief Neon blip → learner sees zero progress/memories; support cannot correlate from logs.

**Suggested fix:** Always `console.warn` with learner id hash; consider discriminated union `{ ok: false, reason }` for API routes to return 503.

**Owner stream:** 02-backend-api

#### R5 — Missing tests for new surface area

**Location:** New exports in `neon-db.ts`; route changes

**Issue:** No `vitest` coverage for advisory lock helpers, mapper shape, or route auth/db branches.

**Failure scenario:** Mapper drops `concept_name_he` parity or lock `finally` removed in future edit — undetected until production.

**Suggested fix:** Unit test `mapDashboardSnapshotToLearnerDashboard` against fixture snapshot; document integration test requirement for lock behavior under Neon.

**Owner stream:** 02-backend-api / 08-evals

---

## Silent-function / dead-code audit

| Symbol | Location | Status | Notes |
|--------|----------|--------|-------|
| `tryLearnerAdvisoryLock` | `neon-db.ts:42` | **used** | `generateLearningPlan`, `consolidateLearnerMemory` |
| `releaseLearnerAdvisoryLock` | `neon-db.ts:51` | **used** | `finally` in both callers |
| `mapDashboardSnapshotToLearnerDashboard` | `neon-db.ts:2454` | **used** | `/api/dashboard` only |
| `getMemoryTimelineFromNeon` | `neon-db.ts:2857` | **used** | `/api/memory` (pre-existed; newly wired) |
| `fetchDashboard` | `data.ts:64` | **dead** | No importers after route migration |
| `fetchMemories` | `data.ts:110` | **dead** | No importers after route migration |
| `useDashboardQuery` / `useMemoriesQuery` | `use-learner-data.ts` | **unused hooks** | Pre-existing; not introduced by this diff |

---

## Edge-case matrix

| Case | Handled? | Evidence |
|------|----------|----------|
| `dbConfigured === false` | partial | Routes return empty 200 (R3); consolidator returns `{ ran: false, reason: 'db_unavailable' }` |
| Unauthenticated request | yes | Both routes: 401 if no Clerk user or `getAuthContext()` null |
| Empty learner data (new user) | yes | Snapshot returns `EMPTY_DASHBOARD`; memory returns `[]` — intentional |
| Concurrent write (same learner) | partial | Lock added (R1 — may not hold cross-instance) |
| Invalid / missing input | n/a | GET routes; no body params |
| Lock contention (same learner) | yes | Plan throws; consolidation returns `consolidation_in_progress` |
| LLM failure during consolidation | yes | Returns `llm_unavailable_or_parse_failed`; lock released in `finally` |
| Cron overlap Vercel + GHA | yes | GHA schedule removed; manual backstop only |

---

## Test assessment

| Change area | Tests exist? | Assert behavior? | Gap |
|-------------|--------------|------------------|-----|
| Advisory locks | no | — | R5 |
| `mapDashboardSnapshotToLearnerDashboard` | no | — | R5 |
| `/api/dashboard` Neon path | no | — | Route integration or handler test |
| `/api/memory` Neon path | no | — | Same |
| `generateLearningPlan` lock throw | no | — | `plan-neon.integration.test.ts` exists but needs Neon; doesn't assert lock |
| GHA cron dedupe | no | n/a | Config-only; verify in deploy checklist |

---

## Clarity & complexity

- Lock helpers are small, well-named, and correctly use `finally` for release — good.
- `mapDashboardSnapshotToLearnerDashboard` is appropriately thin; `est_minutes ?? 20` is a reasonable legacy default but undocumented (NIT).
- `generateLearningPlan` persist block indentation in the diff is correct; function remains large (~160 lines for persist loop) — pre-existing complexity, not introduced by this change alone.

---

## Escalations (other streams)

| Finding ID | Escalate to | Reason |
|------------|-------------|--------|
| R1, R2 | **24-architecture** | Locking strategy + transactional plan writes align with assessment F2; may need ADR amendment |
| R1, R2 | **07-curriculum** | Planner unification (ADR-0007) should pick one persist + lock pattern |
| R3, R4 | **09-infra** | Observability when `DATABASE_URL` missing or Neon degraded |
| — | **24-architecture** | Update `docs/architecture/current-state.md` — still lists Render paths for dashboard/memory |

---

## Recommended follow-ups

1. **Before next planner work:** Implement transactional lock + persist (R1 + R2) or document accepted race window in ADR.
2. **Quick win:** Align dashboard/memory `dbConfigured` branch with 503 pattern (R3).
3. **After merge:** Delete or deprecate `fetchDashboard` / `fetchMemories` (R6).
4. **Add** unit test for `mapDashboardSnapshotToLearnerDashboard` (R5).
5. **Update** `docs/architecture/current-state.md` table for Neon-direct dashboard/memory routes.

---

## References

- Diff: uncommitted changes on `main` (11 modified files in coordinator scope)
- Related assessment: `docs/architecture/assessments/2026-07-05-platform-overview.md` (F2 plan race, F3 consolidation race, F4 legacy API)
- Skills: `.cursor/skills/code-review/SKILL.md`, `.cursor/skills/neon-direct-route/SKILL.md`
