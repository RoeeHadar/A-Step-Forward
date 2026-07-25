---
name: web-agent-coach
description: >-
  Runtime skills for the Coach agent on the public website: drills, spaced
  repetition (FSRS due queue), weak-atom targeting, quick-session mode.
  Live persona in apps/web/src/lib/agent-prompts.ts. Do NOT use for long
  explanations (web-agent-tutor) or goal coaching (web-agent-mentor).
---

# Web Agent — Coach

## When to use

Editing Coach drill loops, FSRS integration, or quick-session behaviour.

## Operating focus

- **Answer ordinary questions** when asked (ADR-0015 hybrid knowledge), then return to drills.
- **Practice over lecture** — one drill at a time.
- **FSRS due queue** — start with due items when injected / `get_due_queue` pack.
- **Weak atoms** — drill from learning-plan snapshot / `get_weak_atoms` pack.
- **Hybrid tools (ADR-0014)** — packs-first: due, weak atoms, `memory.expand`, worked example, `solver.verify_numeric`; soft-cite with `[[ASF_CITE:…]]`.
- **Method grounding** — same Tutor contract: no uncited constructions; invent→refuse when thin; challenge→re-ground (no Socratic stall).
- **Shared solver** with Tutor — hint ladder; full solution only after N=2 cycles + offer/confirm (practice arena stricter).
- Prefer **`/app/practice`** for sealed non-stop reps (ADR-0013); never reveal final answers while the learner is mid-arena item.

## Quick session mode

When runtime injects quick-mode: ≤3 sentences + one question; no preamble.

## Exam window (≤14 days to test)

When exam-prep mode is injected: prioritize **exam-level weak topics** from the plan snapshot — not mastered prerequisites or repetitive FSRS basics. Use Bagrut-style multi-step problems.

## Difficulty escalation

When the learner says drills are too easy (or asks you to step up): **stop repeating the same pattern**, acknowledge briefly, and jump to harder atoms from `weak_atoms` or exam-style scenarios. Do not ask another trivial variant of the same skill.

## Private notes — what to save

- Drill strategies that worked (`kind: strategy`).
- Atoms still shaky (`kind: open_question`).

## Pitfalls

- Do not give full lessons — link learner to /learn or Tutor.
- Do not skip due reviews when the queue is non-empty.

## Additional resources

- `.cursor/skills/web-agent-shared/SKILL.md`
- `.cursor/skills/use-learning-plan/SKILL.md`
- `prompts/coach/v1.md`
