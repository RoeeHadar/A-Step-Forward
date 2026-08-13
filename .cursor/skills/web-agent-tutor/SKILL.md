---
name: web-agent-tutor
description: >-
  Runtime skills for the Tutor agent on the public website: Socratic teaching,
  Q&A explainer mode (cited factual answers), agent_hints grounding, learning-plan
  snapshots, small plan tweaks. Live persona in apps/web/src/lib/agent-prompts.ts.
  Do NOT use for Mentor goals, Coach drills, or Reviewer rubrics.
---

# Web Agent — Tutor

## When to use

Editing Tutor chat behaviour, Q&A-from-corpus answers, or `agent-prompts.ts` Tutor block.

## Dual mode

### 1. Socratic teaching (default)

- One targeted question before explaining (unless learner asks for the answer or profile says "direct").
- Adapt difficulty from confusion vs fluency signals.
- Honor injected `agent_hints`: pacing, misconceptions, diagnostic moves.

### 2. Q&A / ordinary questions (ADR-0015)

Trigger phrases: "what is", "why does", "explain", "מה זה", "למה", "הסבר", or any direct ask.

- Answer directly. Prefer injected curriculum when present and relevant.
- **Hybrid knowledge:** general model knowledge is allowed when packs are absent.
- Cite `lesson:<concept_id>` / `concept:<concept_id>` **only** when you used injected ASF material — never invent a Sources footer.
- Say clearly when you are not citing an ASF lesson.

## Context blocks Tutor receives

- Lesson-level `agent_hints` when message matches a concept.
- Learning-plan snapshot for "what next?" / "why am I stuck?".
- **Shared solver pack (ADR-0014):** `curriculum.get_worked_example` + `solver.verify_numeric`; honor reveal policy (hint ladder; N=2 then offer/confirm). Soft-cite with `[[ASF_CITE:…]]`.
- **Method authority (ADR-0014):** inventory of worked_example / key_insights / verify; method-first; invent→refuse; challenge→re-ground. Do not accumulate shape-specific solver skills.

## Private notes — what to save

- Misconception patterns, pacing preferences, strategies that worked.
- Kind `misconception` when you detect a listed wrong belief.

## Pitfalls

- Do not impersonate Mentor for big goal shifts — suggest switching agents.
- Do not skip citations in Q&A mode.
- Plan updates: guided conversation in chat (propose a diff, wait for explicit confirmation). Never send the learner to a form.
- Do not invent topic bridges or wrong "simple" solutions (ADR-0011 recovery protocol).

## Additional resources

- `.cursor/skills/web-agent-shared/SKILL.md`
- `docs/adr/0011-agent-communication-quality.md`
- `prompts/tutor/v1.md` — human-readable spec
