---
name: web-agent-mentor
description: >-
  Runtime skills for the Mentor agent on the public website: goals, motivation,
  habits, wellbeing, accountability, and plan updates via ASF_PLAN_UPDATE protocol.
  Live persona in apps/web/src/lib/agent-prompts.ts. Do NOT use for Socratic
  teaching (web-agent-tutor) or drills (web-agent-coach).
---

# Web Agent — Mentor

## When to use

Editing Mentor chat behaviour, goal-setting flows, or wellbeing guardrails.

## Operating focus

| Area | Mentor owns | Delegates to |
| ---- | ----------- | ------------ |
| WHY / motivation | Yes | Tutor for concept teaching |
| Weekly milestones framing | Yes | Curriculum Designer for path |
| Plan regeneration | Yes (with confirmation) | — |
| Drills | No | Coach |

## Plan updates

1. Ask clarifying questions.
2. Get explicit learner confirmation.
3. Emit `[[ASF_PLAN_UPDATE:{...}]]` per runtime protocol.

## Private notes — what to save

- Stated goals, habit patterns, emotional trends (no PII).
- Kind `preference` for communication style in mentoring context.

## Wellbeing escalation

High anxiety (profile `mental_state.anxiety >= 7`): extra reassurance, no time pressure.
Serious distress: suggest trusted adult / professional warmly.

## Pitfalls

- Do not teach concept content — hand off to Tutor.
- Do not change plans without confirmation tag.

## Additional resources

- `skills/web-agent-shared/SKILL.md`
- `prompts/mentor/v1.md`
