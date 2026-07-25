---
name: web-agent-shared
description: >-
  Shared runtime skills for all four live website chat agents (Tutor, Mentor,
  Coach, Reviewer): memory hygiene, bilingual rules, math LTR, hybrid knowledge
  (ADR-0015), citations only when ASF packs used, plan-change protocol, safety.
  Injected via apps/web/src/lib/agent-skills.ts on every chat turn. Pair with
  web-agent-tutor, web-agent-mentor, web-agent-coach, web-agent-reviewer.
---

# Web Agent — Shared Skills

## When to use

Editing anything that applies to **every** live website agent: memory writes,
language rules, plan templates, or the shared skill block in `agent-skills.ts`.

## Memory hygiene

| Layer | Scope | Writer | Reader |
| ----- | ----- | ------ | ------ |
| Shared persona | per-learner | Memory Steward + rare agent writes | Every agent, every turn (when relevant) |
| Private notes | per-(learner, agent) | That agent only | That agent only, relevance-filtered |

### Writing private notes

```
POST /api/agent-memory/notes
{ agent, content, importance: 1-5, kind?, related_concept_id? }
```

Kinds: `observation`, `preference`, `strategy`, `open_question`, `misconception`, `win`, `plan`.

- Hard cap: 600 chars per note.
- Importance 5 = must influence next sessions; 1 = nice-to-have.
- Notes are **hints**; the current learner message wins on conflicts (ADR-0015).

### Dreaming schedule (async, off hot path)

| Pass | Endpoint | LLM | Schedule |
| ---- | -------- | --- | -------- |
| Lightweight | `/api/cron/dream-memory` | No | Monday 00:00 UTC (Vercel cron) |
| Heavy | `/api/cron/consolidate-memory` | Yes (cheap tier) | Monday 02:00 UTC |

## Bilingual + math + language (ADR-0015)

- Resolve language once per turn: explicit request → latest substantive message → profile → UI locale.
- Math always LTR in `$...$` / `$$...$$`.
- No external links.

## Hybrid knowledge (ADR-0015)

- **Default:** answer from general model knowledge.
- **When ASF packs are injected and relevant:** treat plan / profile / mastery / curriculum as authoritative.
- Cite `lesson:<id>` / `concept:<id>` **only** when you materially used injected ASF material — never invent citations.
- Ordinary questions must not dump status/plan/memory.

## Communication quality (ADR-0011 / ADR-0012 / ADR-0015)

- **Anti-filler:** ban stock closers; on continue, resume unfinished steps.
- **Status:** paraphrase bilingual briefing + AUTHORITATIVE pack when injected for status turns; never dump XP/ISO/raw keys; never ~100% bagrut guarantees.
- **Pressure (ADR-0012):** validate → honest status → ONE next step from pack → offer to start.
- **Recovery:** simplest *correct* method (corpus if present, else honest general knowledge).
- Live contract: `agent-skills.ts` + `chat-context-needs.ts` + `chat-response-quality.ts` + intents in `learner-chat-intent.ts`.
- Quality gate: buffered draft → score → one repair retry before stream (no post-display appends).

## Hybrid tools + memory digests (ADR-0014)

- Server tool packs + `[[ASF_*]]` markers; soft-cite when packs used.
- Method grounding: prefer injected worked examples; if packs thin, answer generally and say so.

## Plan changes

Learning plans update **only** via the official template from Tutor chat sidebar.

## Pitfalls

- Do not stuff raw chat history into notes — clip insights only.
- Do not write PII into persona or notes.
- Do not let irrelevant Active week / status packs hijack a math question.
