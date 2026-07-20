# Cohort pilot synthesis — agent walkthrough wave
Date: 2026-07-21  
Mode: **roleplay: agent** (proxy feedback — not sacred; guides next eng wave)  
Site: https://a-step-forward-waij.vercel.app

## 1. Scoreboard

| Persona | Avg (scored) | Recommend? | Core blocker? |
|---------|--------------|------------|---------------|
| S1 | 3.4 | yes w/ caveats | no (onboarding mid) |
| S2 | 3.5 | yes | no |
| S3 | 3.6 | yes | no |
| S4 | 3.5 | yes | no |
| S5 | 3.4 | yes | no |
| S6 | 3.3 | yes | no |
| S7 | 3.7 | yes | no |
| S8 | 3.6 | yes | no |
| S9 | 3.8 | yes | no |
| S10 | 3.7 | yes | no |
| **T1** | 3.8 | yes | no |

Students ≥3.5: **8 / 10**  
Teacher avg: **3.8**  
Unresolved core-path blockers: **0**

### Outcome: **Win** (iterate)

Meets ≥7/10 ≥3.5 + teacher ≥3.5 + no core blockers. Several UX/plan-fit themes need targeted work.

## 2. Themes (≥3 mentions / strong evidence)

| Theme | Count | Axis | Evidence |
|-------|-------|------|----------|
| Plan level mismatch for 5pt mid-journey | 3+ | plan fit | S7 `building` week shows 3pt foundations (מרובעים יסודות) while goal is bagrut_math_5; Tutor echoes same list |
| Chat transcript empty-state vs visible reply | 2+ | UI / agents | Tutor replied in HE grounded to plan, but UI still showed "אין הודעות עדיין" |
| Clerk new-device OTP friction | ops | auth | Required `+clerk_test` + `424242` for automation; real humans need email OTP |
| Friends + teacher link work when provisioned | + | social | S7 friends list (3); teacher chip on /app; 10 accepted links in DB |
| Educator shell solid | + | teacher | Empty→linked path; notes/hours actionable |

Parking lot: readiness banner not clearly spotted on S7 /app first paint; Vercel Encrypted DATABASE_URL empty on CLI pull.

## 3. Backlog buckets

### P0 bugs
- (none on core path for this wave)

### UX friction
1. Chat message list empty-state conflicting with rendered assistant answer  
2. Onboarding "הבא" stays disabled until many fields filled — unclear which field unlocks (S1)

### Content / plan-fit
3. Seeded/building 5pt plans scheduling low-level 3pt concepts — hurts trust for successful/fast personas  
4. Fresh onboarding still required for non-seeded; OK, but long for short-track testers

### Missing teacher capabilities
5. No first-class "assign / push quiz to student" (expected; mark missing) — reopen/grade path exists in UI  
6. Teacher feedback field on attempts is JSONB — plain HE string write via SQL failed (product expects structured feedback)

### Wontfix / out of scope
- Clerk Development mode badge on prod URL — instance config, not app UI  
- Full 45–180 min human depth per persona — deferred to next human wave

## 4. Top 5 changes (next eng wave)

1. **Fix plan frontier selection for bagrut_math_5 mid-mastery** so weekly cards match 5pt depth (not 3pt foundations) when coverage is already ~80%  
2. **Fix chat empty-state** so "אין הודעות" never shows when messages exist  
3. **Surface readiness / pacing badge more prominently** on /app for seeded phases (building / at-risk / day-before)  
4. **Teacher: structured test feedback UI** already exists — document + smoke; add "assign quiz" only if product wants it  
5. **Onboarding affordance**: show which required fields block "הבא"

## 5. Ops notes

- Correct Neon host: `ep-plain-sea-…` (from `.database-url.local`). Wrong empty Neon was briefly pasted (`ep-falling-cherry-…`).  
- Scripts: `provision-cohort-accounts`, `seed-cohort-pilot`, `provision-cohort-social`  
- Hold accounts ~2 weeks then full reset

## 6. Sign-off

Pilot lead / agent: Auto (Composer) — 2026-07-21  
Human confirmation of scores: pending (agent proxy)
