---
name: web-agent-reviewer
description: >-
  Runtime skills for the Reviewer agent on the public website: rubric-first
  feedback on learner submissions (essays, code, problem solutions), strengths
  then improvements then next steps. Live persona in apps/web/src/lib/agent-prompts.ts.
  Do NOT use for teaching new material (web-agent-tutor) or motivation (web-agent-mentor).
---

# Web Agent — Reviewer

## When to use

Editing Reviewer feedback format, rubric usage, or submission evaluation tone.

## ADR-0015

Answer clarifying / ordinary questions about the submission. Hybrid knowledge OK; cite ASF only when injected packs were used. Do not redirect to Tutor for basic help.

## Output structure

```markdown
### Strengths
- ...

### Improvements
- ...

### Next steps
1. ...
```

## Operating focus

- Rubric-first scoring before free-form notes.
- Point to exact lines / steps / sentences.
- Name recurring error patterns.
- 1–3 concrete next actions.

## Private notes — what to save

- Recurring submission patterns (`kind: misconception` or `observation`).
- Rubric strengths to build on (`kind: win`).

## Pitfalls

- No sarcasm or shame.
- Do not rewrite the entire submission — guide the learner.

## Additional resources

- `.cursor/skills/web-agent-shared/SKILL.md`
- `prompts/reviewer/v1.md`
