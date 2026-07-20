# Agent walkthrough notes (live)

updated: 2026-07-20T21:55+03:00
mode: roleplay agent
otp: "424242"  # Clerk +clerk_test emails
emails: asf.pilot.<id>+clerk_test@example.com

## Completed
- [x] T1 signed in (password + OTP 424242)
- [x] T1 identity → educator `pilot_teacher_asf`
- [x] T1 landed `/educator` — roster empty, invite UI OK, about-me OK
- [x] S1 signed in + identity `pilot_s1_math3` → redirected to **/onboarding** (step 1 goals)

## In progress
- [ ] S1 finish onboarding → lesson → quiz → tutor
- [ ] S2–S10 same pattern
- [ ] Teacher invites + scripted actions
- [ ] Forms + synthesis

## Blockers remaining
- DATABASE_URL empty from Vercel Encrypted pull → no mid-journey seeds (all fresh onboarding)
  Fix: paste from Neon/Vercel per `get-database-url.md` (optional for continuing)

## UX notes so far
- Educator dashboard Hebrew clear; empty state honest ("עדיין אין תלמידים")
- Identity role picker clear (learner vs teacher)
- Clerk new-device challenge: use `+clerk_test` emails + OTP **424242**
- Onboarding step 1 loads (subjects, grade, dates) — Next disabled until required fields filled
