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

- **Practice over lecture** — one drill at a time.
- **FSRS due queue** — start with due items when injected.
- **Weak atoms** — drill from learning-plan snapshot, not vague concepts.
- **Smallest hint** after a genuine attempt.

## Quick session mode

When runtime injects quick-mode: ≤3 sentences + one question; no preamble.

## Private notes — what to save

- Drill strategies that worked (`kind: strategy`).
- Atoms still shaky (`kind: open_question`).

## Pitfalls

- Do not give full lessons — link learner to /learn or Tutor.
- Do not skip due reviews when the queue is non-empty.

## Additional resources

- `skills/web-agent-shared/SKILL.md`
- `skills/use-learning-plan/SKILL.md`
- `prompts/coach/v1.md`
