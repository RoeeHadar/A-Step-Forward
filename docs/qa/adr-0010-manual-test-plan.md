# ADR-0010 — Manual test plan (assessment-driven progression)

Maps every ADR-0010 decision to a **seed variant → steps → expected result**, so the
onboarding → final-exam journey can be walked deterministically. Pair with
[ADR-0010](../adr/0010-assessment-driven-progression.md) and
[ADR-0009](../adr/0009-goal-paced-adaptive-planning.md).

## Setup

Seed a state with the reusable ops script (never commit the URL):

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'          # local corporate-proxy TLS only
$env:DATABASE_URL='<prod Neon URL>'
node scripts/seed-pilot-demo.mjs --variant <variant>
$env:DATABASE_URL=$null; $env:NODE_TLS_REJECT_UNAUTHORIZED=$null
```

Variants: `fresh`, `building` (default), `at-risk`, `near-exam`, `day-before`, `goal-complete`.
One account = one state at a time; re-run to flip. Hard-refresh `/app` after each seed.
Pilot account: `roeehadar@gmail.com` (`user_3Fakzy…`), goal `bagrut_math_5`.

## Test matrix

| # | ADR-0010 decision | Variant | Steps | Expected |
|---|---|---|---|---|
| 1 | Readiness is humble, never 100% | `near-exam` | Open `/app`, read pacing banner | Readiness ~95%, **not** 100%; positive-but-cautious note |
| 2 | Readiness is mock-gated | `building` | Read banner (no passed mock) | Readiness capped ~70% + "sit a mock exam" note |
| 3 | Passing a mock ungates readiness | `building` → sit a mock and pass | Take mock from `/app`, score ≥ 60% | Readiness jumps above 70%; note changes; mock appears in **My Tests** |
| 4 | Concave curve (top gains cost more) | `fresh` vs `building` vs `near-exam` | Compare readiness across three seeds | ~0% → ~70% → ~95%; the 82→96% critical step yields a smaller readiness bump than 0→82% |
| 5 | Final-phase = theory + Mentor | `day-before` | Open `/app` | "Review theory + talk to your Mentor" note; no new material pushed |
| 6 | Foundational start, no regression | `fresh` | Open `/app`, view week 1 concepts | Plan starts at foundations; advanced concepts not scheduled first |
| 7 | Pacing: behind → triage badge | `at-risk` | Read pacing badge | Amber **"Behind pace"** / at-risk badge (required velocity > capacity) |
| 8 | Pacing: ahead / maintenance | `goal-complete` | Read pacing badge | **"Ahead"**; remaining scope ~0; review/maintenance week |
| 9 | Earned advancement (lessons ≠ advance) | `building` | Mark all week-1 lessons complete, reload `/app` | Week does **not** advance; still on week 1 (lessons give exposure only) |
| 10 | Weekly gate: pass criteria (critical floor) | `building` | Take week-1 quiz; score high overall but miss a critical topic | **Fails** the gate even with a good average (critical concept below 0.6 floor) |
| 11 | Gate pass → advance + re-pace | `building` | Take week-1 quiz and pass (aggregate ≥ 0.75, all critical ≥ 0.6), reload `/app` | Week 1 marked completed; plan advances to week 2; concepts re-paced |
| 12 | Retake rotation (anti-gaming) | `building` | Fail week-1 quiz, immediately retake | Retake shows **fresh questions**, not the identical set |
| 13 | Fail → remediation carry-forward | `building` | Fail with a weak critical topic, then advance via override | Weak concept(s) re-scheduled into the next week |
| 14 | Soft override (never stranded) | `building` | Attempt the weekly gate 3× without passing | Plan advances anyway (retakes exhausted); weak topics carried forward |
| 15 | Tests archive (history + review) | `near-exam` | Open **My Tests** → open the mock | List shows kind-aware label + pass/fail + date; detail shows per-topic bars + question review (MCQ colored, open items show free text) |
| 16 | Wellbeing modulates load, not the bar | `building` (+ high-anxiety profile) | Compare weekly_load with/without wellbeing bias | Fewer new concepts per week when bias active; the **pass threshold is unchanged** |

## Notes / known gaps

- Numbers (70/95%, thresholds) are display-time; exact values may drift slightly with decay and live pacing math — trends and gating decisions are what matter.
- Deferred UI follow-ups (not blocking): explicit "remediation" flag chip and a "pass to continue" affordance on the plan card (tracked in ADR-0010 Stream A follow-ups).
- Calibration guardrails are pinned as unit tests in `apps/web/src/lib/assessment-calibration.test.ts` — run `pnpm --filter @asf/web test` to confirm gate/decay/readiness invariants before shipping changes to these paths.
