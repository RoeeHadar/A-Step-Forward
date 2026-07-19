---
name: web-agent-shared
description: >-
  Shared runtime skills for all four live website chat agents (Tutor, Mentor,
  Coach, Reviewer): memory hygiene, bilingual rules, math LTR, corpus citations,
  plan-change protocol, safety. Injected via apps/web/src/lib/agent-skills.ts on
  every chat turn. Pair with web-agent-tutor, web-agent-mentor, web-agent-coach,
  web-agent-reviewer.
---

# Web Agent — Shared Skills

## When to use

Editing anything that applies to **every** live website agent: memory writes,
language rules, plan templates, or the shared skill block in `agent-skills.ts`.

## Memory hygiene

| Layer | Scope | Writer | Reader |
| ----- | ----- | ------ | ------ |
| Shared persona | per-learner | Memory Steward + rare agent writes | Every agent, every turn |
| Private notes | per-(learner, agent) | That agent only | That agent only, top-6 |

### Writing private notes

```
POST /api/agent-memory/notes
{ agent, content, importance: 1-5, kind?, related_concept_id? }
```

Kinds: `observation`, `preference`, `strategy`, `open_question`, `misconception`, `win`, `plan`.

- Hard cap: 600 chars per note.
- Importance 5 = must influence next sessions; 1 = nice-to-have.
- Do not duplicate what belongs in shared persona (HOW they learn) vs mastery (WHAT they know).

### Dreaming schedule (async, off hot path)

| Pass | Endpoint | LLM | Schedule |
| ---- | -------- | --- | -------- |
| Lightweight | `/api/cron/dream-memory` | No | Monday 00:00 UTC (Vercel cron) |
| Heavy | `/api/cron/consolidate-memory` | Yes (cheap tier) | Monday 02:00 UTC |

Lightweight pass: Jaccard dedupe + cap at 30 live notes per agent.
Heavy pass: promotes durable notes into shared persona (min 6 notes).

## Bilingual + math

- Hebrew default; mirror learner's last message language.
- Math always LTR in `$...$` / `$$...$$`.
- No external links; cite `lesson:<id>` and `concept:<id>` only.

## Plan changes

Learning plans update **only** via the official template from Tutor chat sidebar.
Never claim a plan changed from casual conversation.

## Pitfalls

- Do not stuff raw chat history into notes — clip insights only.
- Do not write PII into persona or notes.
- Do not run dreaming inline on the chat request path.

## Additional resources

- `.cursor/skills/agent-skill-notes/SKILL.md` — note schema and top-K read contract
- `.cursor/skills/learner-persona/SKILL.md` — shared persona rules
- `.cursor/skills/dreaming-and-consolidation/SKILL.md` — full dreaming pipeline
