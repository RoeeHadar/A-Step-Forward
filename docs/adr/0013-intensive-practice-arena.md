# ADR 0013: Intensive practice arena

- **Status:** Accepted
- **Date:** 2026-07-23
- **Deciders:** Product owner + Composer (grilling session)
- **Related:** [ADR-0011](0011-agent-communication-quality.md), [ADR-0012](0012-agent-context-under-pressure.md), custom quiz seal pattern

## Context

Learners currently get exercises mainly inside lessons and as timed custom quizzes. They need a **continuous practice arena**: non-stop reps at the right topic and level, with teacher-style hints that never expose the answer until submit or give-up. This is a core foundation surface, distinct from teach-then-practice lessons and exam-like timed quizzes.

## Decision

### Product

1. First-class surface **`/app/practice`** (also `/practice` → redirect): one item at a time, infinite queue feel, soft session goals (~10 items / ~15 min).
2. **Coach** owns the arena voice; optional scoped Coach chat with a hard no-answer contract. Tutor stays for theory/lessons.
3. Queue is **server-owned**: weak atoms under active plan week → planner/weak concepts → difficulty from recent success; optional concept narrow. Bootstrap from onboarding subjects/goal if no plan.
4. **Corpus-first** authored closed questions; **LLM ephemeral fill** when the bank is thin (same seal pattern as custom quiz).
5. **Hint ladder** (3 steps: concept → strategy → scaffold). Full solution only after submit or give-up.
6. Wave 1 is **closed-first** (mcq, true/false, numeric, short_answer / fill_blank). Mastery + light XP via existing helpers.
7. Keys and unused hints never leave Neon until authorized.

### Wave 1 out of scope

Explore-outside-plan default, open-heavy Reviewer grading, separate points currency, FSRS-due-only as the only mode, social streaks.

## Consequences

**Positive:** Learners can grind deliberately; hints stay honest; mastery/XP stay unified.

**Risks:** LLM fill cost/latency — throttle per session; intent to keep corpus coverage growing.

## Alternatives considered

- Fold into `/app/quiz` as a mode — rejected (different job: timed set vs endless reps).
- Ladder-only with no Coach chat in v1 — deferred; wave 1 includes ladder + deep-link to Coach with contract.
- Authored-only until banks grow — rejected for “non-stop” volume; hybrid wins.
