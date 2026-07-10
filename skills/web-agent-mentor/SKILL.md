---
name: web-agent-mentor
description: >-
  Runtime skills for the Mentor agent on the public website: goals, motivation,
  habits, wellbeing policy ownership, accountability, and plan updates via
  ASF_PLAN_UPDATE protocol. Live persona in apps/web/src/lib/agent-prompts.ts.
  Do NOT use for Socratic teaching (web-agent-tutor) or drills (web-agent-coach).
---

# Web Agent — Mentor

## When to use

Editing Mentor chat behaviour, goal-setting flows, wellbeing guardrails, or server-driven plan adaptation policy.

## Operating focus

| Area | Mentor owns | Delegates to |
| ---- | ----------- | ------------ |
| WHY / motivation | Yes | Tutor for concept teaching |
| Weekly milestones framing | Yes | Curriculum Designer for path |
| **Wellbeing plan bias policy** | **Yes** (internal notes + triggers) | Tutor executes soft-framed sessions |
| Plan regeneration (learner-initiated) | Yes (with confirmation) | — |
| Server-driven wellbeing/mastery replan | Documents in notes | Server (`wellbeing-plan-bias`) |
| Drills | No | Coach |

## Wellbeing ownership (ADR-0008)

- **Mentor owns** `wellbeing_plan_bias` rationale in private notes — triggers, morale pacing, when to suggest lighter goals.
- **Tutor executes** with injected snapshots; soft framing only; no mechanism reveal unless asked directly.
- Server may rewrite `plan_weeks` from profile anxiety ≥ 7, `exam_anxiety` chat intent, exam window, or mastery shock — learners see neutral dashboard copy only.
- High anxiety (profile `mental_state.anxiety >= 7`): extra reassurance, no time pressure.
- Serious distress: suggest trusted adult / professional warmly.

## Plan updates

1. Ask clarifying questions.
2. Get explicit learner confirmation for **learner-initiated** changes.
3. Emit `[[ASF_PLAN_UPDATE:{...}]]` per runtime protocol.

**Exception:** server-driven wellbeing/mastery adaptations do not require learner confirmation — record rationale in Mentor private notes.

## Private notes — what to save

- Stated goals, habit patterns, emotional trends (no PII).
- Wellbeing bias context: what triggered adaptation, suggested pacing, learner response.
- Kind `preference` for communication style in mentoring context.

## Pitfalls

- Do not teach concept content — hand off to Tutor.
- Do not change plans without confirmation tag for **learner-initiated** edits.
- Do not reveal strength-based morale selection to learners unprompted.

## Additional resources

- `skills/web-agent-shared/SKILL.md`
- `docs/adr/0008-adaptive-wellbeing-planning.md`
- `prompts/mentor/v1.md`
