---
name: diagnostic-plan-golden-path
description: >
  Golden path for onboarding → first learning plan (rolling 2-week window) and
  the Jul 2026 trial-and-error log of what failed vs worked. READ THIS before
  changing onboarding submit, plan generation, diagnostic, or "Creating plan…" UX
  — especially if you see FUNCTION_INVOCATION_TIMEOUT or a climbing timer.
---

# Onboarding → rolling plan golden path (Vercel / Neon)

## End-to-end contract (current — works)

```
/onboarding (4 steps: goals → background → motivation → tutor style)
  └─ POST /api/onboarding/submit
       └─ bootstrapOnboardingPlan()  ← thin module ONLY
            apps/web/src/lib/onboarding-plan-bootstrap.ts
            ├─ profile upsert
            ├─ ≤8 mastery seeds
            ├─ DELETE old plans (no advisory lock)
            └─ INSERT plan + 2 weeks (≤4 concepts each)
  └─ client → /app if has_plan; on 25s abort → /plan-setup

/plan-setup → POST /api/plans/bootstrap (same thin path)
/diagnostic → redirects to /plan-setup (legacy; no MCQ gate)
GET /api/plans/current → advanceRollingPlanWindow when week past due
```

**Target SLO:** submit returns with `has_plan: true` in **< 5–10s**.

### Hard rules (never violate)

1. **Never import `neon-db.ts` from onboarding/submit or plans/bootstrap.**  
   It pulls `kg-data.json` (~325KB) + plan-worklist + learning-plan. Cold start alone can blow the Vercel budget; combined with locks it hung until `FUNCTION_INVOCATION_TIMEOUT`.
2. **Never use advisory-lock + `1/0` Neon HTTP transactions on the first-plan path.**  
   `pg_try_advisory_xact_lock` with division-by-zero abort hung under contention.
3. **Materialize only 2 weeks × ≤4 concepts on first create.**  
   Full exam-horizon calendars (12–24 weeks) timed out even after “fast path” attempts.
4. **Verify `has_plan` (and ideally week rows) before telling the client success.**  
   Redirect to `/app` only when the plan row exists.
5. **Further calibration happens while learning** — no post-onboarding diagnostic questionnaire gate.

---

## Trial-and-error walkthrough (Jul 2026) — learn from this

Chronological log of what we tried, what broke, and what finally worked.  
Use this as a stepping stone before inventing a “smarter” first-plan path.

### Phase A — Diagnostic questions broken

| Attempt | Result |
|---------|--------|
| Mark stems “asked” on **serve** | Queue drained → **zero questions** |
| Resume stale **active** sessions as complete | Skipped straight to plan with wrong counts |
| Trust legacy `question_idx` for UI progress | Counter started at Q5; completion said 7 after ~3 answers |
| 12-question sessions on thin bank | Duplicates, exhaustion, timeouts |
| **Fix that worked:** fresh session (pending-only resume), mark asked on **answer**, client step from `responses.length`, **6** MCQs from available bank | Questions OK |

### Phase B — Plan stuck on “Creating…” (timer 60–76s+)

| Attempt | Result |
|---------|--------|
| `ensureLearningPlan` + lock poll / retry on “already in progress” | Retry storms; still stuck |
| Client 55s fetch abort then poll `exists=1` up to 120s | Timer climbed; `has_plan` never flipped |
| `litePlanConcept` return object; generate returns `{ ok, plan_id }` | Helped payload size; **did not** fix hang before INSERT |
| `?fast=1` + `buildFastPlanConceptOrder` (skip BFS) | Better in theory; client/cache often still hit slow path |
| Persist before wellbeing write; skip morale on fast path | Good practice; still timed out |
| Kickoff plan on last diagnostic answer (server-side) | Race with adaptive refresh / still heavy module |
| Auto fast path when no plan exists | Still imported neon-db monolith |
| Cap to **2 rolling weeks** inside `generateLearningPlan` | Correct product model, **still timed out** — root cause was not only week count |
| **Symptom:** Vercel `FUNCTION_INVOCATION_TIMEOUT fra1::…` | Serverless killed the function |

### Phase C — Product change (remove diagnostic gate)

| Change | Result |
|--------|--------|
| Drop self-assessment + diagnostic after goals | Correct product direction |
| Sync `createOnboardingPlan` via neon-db on submit | Still `FUNCTION_INVOCATION_TIMEOUT` |
| Client waits on submit “Creating your plan…” | Same hang, then Vercel error page |

### Phase D — What finally worked

| Change | Why it worked |
|--------|----------------|
| **`onboarding-plan-bootstrap.ts`** — own `neon()` client, only `onboarding-self-score` | No kg-data, no learning-plan BFS, no wellbeing, no advisory locks |
| **`POST /api/onboarding/submit`** imports **only** the bootstrap module | Tiny cold start |
| **`POST /api/plans/bootstrap`** for `/plan-setup` | Same path if submit aborts |
| Client **25s abort → `/plan-setup`** | Recover without infinite timer |
| Rolling window advance later via `advanceRollingPlanWindow` on plan fetch | Deferred work off the critical path |

**Production confirmation:** after deploy `1d44e8cc`, plan creation succeeded.

---

## Rolling window (product model)

| Rule | Why |
|------|-----|
| Materialize **2 weeks** first | What the student sees; keeps writes tiny |
| ≤ **4 concepts / week** | Enough for dashboard; safe under Vercel limits |
| Sequential chunks (week 1 = first concepts) | Pedagogy + latency; not round-robin |
| `advanceRollingPlanWindow` | Past-due active week → complete, promote upcoming, append next from mastery |
| Horizon `end_date` optional | UX for exam timeline; **not** full materialized weeks |

Do **not** regenerate the entire multi-week plan on onboarding. Mid-journey heavy regen only via explicit agent/template/`?full=1` paths that already accept longer latency.

---

## Anti-patterns checklist (do not reintroduce)

- [ ] Import `neon-db` / `kg-data.json` on onboarding or bootstrap routes  
- [ ] Advisory lock + `1/0` on first-plan writes  
- [ ] `buildLearningPlan()` BFS / atom hydration before first INSERT  
- [ ] Textbook/Bagrut hydration before plan row exists  
- [ ] Full 12–24 week calendar on first create  
- [ ] Round-robin concepts across many weeks  
- [ ] Client-only POST with long poll while server never commits  
- [ ] Long `sleep` retry loops inside the submit handler  
- [ ] Resume diagnostic as complete / serve-time stem reservation / `question_idx` UI  
- [ ] Block learning behind a post-onboarding diagnostic questionnaire  

---

## Key files

| Area | Path |
|------|------|
| **Thin bootstrap (source of truth for first plan)** | `apps/web/src/lib/onboarding-plan-bootstrap.ts` |
| Onboarding submit | `apps/web/src/app/api/onboarding/submit/route.ts` |
| Plan-setup bootstrap API | `apps/web/src/app/api/plans/bootstrap/route.ts` |
| Plan-setup UI | `apps/web/src/app/plan-setup/page.tsx` |
| Seed concepts from goal | `apps/web/src/lib/onboarding-self-score.ts` |
| Rolling advance (later) | `neon-db.ts` → `advanceRollingPlanWindow` |
| Exists poll | `GET /api/plans/current?exists=1` |
| Vault log | `obsidian-vault/coordination/streams/diagnostic-plan-fixes.md` |

## Related skills

- `skills/onboarding-flow/SKILL.md` — questionnaire → profile fields  
- `skills/use-learning-plan/SKILL.md` — planner contract for agents (mid-journey)  
- `skills/neon-direct-route/SKILL.md` — Vercel + Neon route patterns  
- `skills/deploy/SKILL.md` — post-push verify  

## Verification

1. Hard refresh (stale client bundles reintroduced old generate paths).  
2. Reset learner or fresh account.  
3. Onboarding → Create plan → `/app` with 2 weeks visible in seconds.  
4. If submit aborts: `/plan-setup` → bootstrap → `/app`.  
