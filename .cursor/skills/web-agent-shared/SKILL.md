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

## Communication quality (ADR-0011 / ADR-0012)

- **Grounding:** non-trivial claims only from injected lesson/concept/`agent_hints`/KG; no invented "X helps with Y" bridges.
- **Anti-filler:** ban stock closers ("אני חושב שזה יעזור", "I need to explain differently"); on continue, resume unfinished steps.
- **Status:** paraphrase bilingual briefing + AUTHORITATIVE learner-facing pack; never dump XP/ISO/raw keys; never ~100% bagrut guarantees; never deny knowing injected plan/status.
- **Pressure (ADR-0012):** validate → honest status → ONE next step from pack → offer to start. No topic menus; no invented replacement plans; never misread `points_group` as completed study. Ban garbage Hebrew ("חשוך", "באחריות", "להביא לדמיון", …).
- **Recovery:** when too hard / simplify — drop failed path, honest plan-scope, simplest *correct* method.
- Live contract: `apps/web/src/lib/agent-skills.ts` + `learner-progress-briefing.ts` + `pressure-next-step.ts` + intents in `learner-chat-intent.ts`.

## Hybrid tools + memory digests (ADR-0014)

- Uniqueness = tool/data allowlists + memory policy (not costume prompts alone).
- Chat path stays text-only LLM; **server tool packs** + `[[ASF_*]]` markers are the hybrid surface.
- Cross-agent memory via **handoff digests** + on-demand `memory.expand` — not raw peer note dumps.
- Persona writes are **role-gated**; Steward consolidate remains the backstop.
- Soft citation: `[[ASF_CITE:{"tools":[…],"concept_id":"…"}]]` (stripped; shadow-logged).

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
