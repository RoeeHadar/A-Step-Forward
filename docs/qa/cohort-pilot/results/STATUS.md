# Cohort pilot — live status

updated: 2026-07-21
wave: cohort-pilot-2026-07
mode: roleplay agent (proxy feedback)

## Workaround note

- **Emails:** `asf.pilot.<id>+clerk_test@example.com` — OTP **424242**
- **Clerk:** `apps/web/.env.local` via `vercel env pull`
- **DATABASE_URL:** use prod Neon (`ep-plain-sea-…` / `.database-url.local`). Empty Neon paste (`ep-falling-cherry-…`) rejected.
- **Password:** `results/.pilot-password.local`

## Pipeline

| Step | Status |
|------|--------|
| Kit | done |
| Clerk accounts ×11 | done |
| Seed S7–S10 | done |
| Identities + teacher links + friends | done (`provision-cohort-social`) |
| Spot UX (S7 /app, friends, tutor; T1 shell) | done |
| Teacher notes + S8 hours | done |
| Feedback forms ×11 | done (agent proxy) |
| Synthesis | done → `results/SYNTHESIS.md` |

## Outcome

**Win (iterate)** — see SYNTHESIS.md top 5 changes.

## Wave A → Wave 2 retest (2026-07-21)

| Step | Status |
|------|--------|
| A1–A3 fixes (subagents) | done (local) |
| W2 accounts T2/R1–R3 | done (`roster-w2.json`, `setup-cohort-w2.mjs`) |
| Browser retest localhost | done |
| Report | done → `results/WAVE2_REPORT.md` (**3/3 PASS**) |

Next: commit/push/deploy Wave A so production matches verified UI, then human pilot.

## Cleanup

Hold ~2 weeks → `reset-learner.mjs --delete-profile` per pilot user (+ optional Clerk delete).
