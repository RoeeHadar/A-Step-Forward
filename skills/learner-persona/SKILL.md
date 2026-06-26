---
name: learner-persona
description: The CLAUDE.md-style, per-learner persona that EVERY agent reads on every turn. How to read it, how (and when) to write to it, what NEVER to put in it. Pair with `skills/chat-memory-context/SKILL.md` (composition order) and `skills/agent-skill-notes/SKILL.md` (per-agent private notes).
---

# Learner Persona

## Purpose

A free-form, markdown-friendly summary of HOW this learner thinks, talks, and learns. Modeled on Anthropic's CLAUDE.md pattern: one durable document that every agent in the network reads as the "what this learner is like" baseline, so a new chat with a different agent doesn't feel like meeting a stranger.

It is **shared** across every agent (tutor, mentor, coach, reviewer, qa_explainer, note_taker, …) — distinct from per-agent private notes (`learner_agent_notes`, separate skill).

## What lives in the persona

- **How they talk.** Casual / formal? Hebrew / English / code-switching? Long messages or terse?
- **How they like explanations.** Worked example first vs. definition first; one analogy vs. step-by-step; pictures vs. equations.
- **Triggers and preferences.** Things that boost engagement (a specific kind of metaphor, a project they care about) and things that derail it (vocabulary, exam pressure cues, anxiety triggers).
- **Recent durable observations.** "Confuses SSS and SSA repeatedly (logged 2026-06-25)" — not "got Q3 wrong today" (that's a per-agent private note).

## What does NOT belong

- ❌ **PII.** No real names, school names, addresses, phone numbers, parent details. The persona is logged and shipped to every LLM call — keep it anonymous-friendly.
- ❌ **Per-session noise.** "Asked about derivatives once" doesn't belong. Recurring patterns do.
- ❌ **Mastery data.** That's `concept_mastery` + `skill_practice`. The persona is HOW, not WHAT.
- ❌ **Plans, weekly schedules.** That's `learning_plans` + `plan_weeks`.
- ❌ **Private agent observations.** Save those to `learner_agent_notes` via the agent-skill-notes skill instead — they let each agent keep its own scratchpad without polluting the shared view.

## Schema

The persona lives on the existing user row, in the same Neon table as the
rest of the learner data (and the Clerk `userId` is the join key — same
storage bucket as the user identity itself):

```sql
ALTER TABLE learner_profiles
  ADD COLUMN learner_persona            TEXT,
  ADD COLUMN learner_persona_updated_at TIMESTAMPTZ;
```

The chat route reads it on every turn and injects it as:

```
## What I know about this learner (shared persona)
<persona body>
```

…between the agent persona and the per-agent private notes (see
`chat-memory-context`).

## Recommended structure (kept short, <= 4000 chars, all clamped)

```markdown
## How they talk
- Casual Hebrew, code-switches to English for math terms.
- Types fast, short messages, hates being told to "elaborate".

## How they like explanations
- Worked example first, THEN the rule.
- Prefers physical / visual intuition over symbolic manipulation.

## Triggers and preferences
- Anxiety spikes within 7 days of an exam → soften tone, smaller steps.
- Engages strongly when math is linked back to a physics setup.
- Hates when the agent says "as we discussed earlier" if they don't recall it.

## Recent durable observations (rolling, last 30d)
- 2026-06-26: confuses SSS / SSA repeatedly across 3 sessions — likely missing the included-vs-non-included angle distinction.
```

## API

```ts
GET    /api/agent-memory/persona
  → { text: string|null, updated_at: string|null }

POST   /api/agent-memory/persona
  body: { text: string }   // full replace, hard-capped to 4000 chars
  → { ok: true }

PATCH  /api/agent-memory/persona
  body: { section: string, line: string }
  // Appends `- <line>` under `## <section>` (creating the section if
  // absent). Idempotent on exact-duplicate bullet lines.
  → { ok: true }
```

All endpoints are scoped to the authenticated Clerk `userId`; you cannot read or write another learner's persona.

## When agents should write

| Trigger                                                                                                    | Action                                                                                                                          |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| You've observed the SAME pattern across ≥ 3 turns in this session AND it's likely to recur across sessions. | `PATCH` with `section: "How they talk"` or `section: "Triggers and preferences"`, `line: <one sentence>`.                       |
| You've identified a HOW-related preference the learner stated explicitly ("I learn better with examples").  | `PATCH` with `section: "How they like explanations"`, `line: <the preference, rephrased third-person>`.                          |
| Dreaming pass / Memory Steward finds a stable pattern in the agent_notes spanning multiple agents.          | `POST` (full replace) the consolidated body. Preserve sections; remove stale lines older than 30d.                              |

Do **not** write on every turn. The persona is durable, not a chat log.

## When agents should NOT write

- A single observation from a single turn. Wait until the pattern recurs.
- Anything attached to a specific concept or skill atom — that's mastery / atom-practice data, not persona.
- Anything you'd be embarrassed for a *parent* / *educator* / the learner themselves to read on a future "view my profile" page. Persona is logically public-to-the-learner.

## Pitfalls

- ❌ Wholesale rewriting from a single agent on every turn. Treat the persona as append-mostly until a real consolidation pass.
- ❌ Forgetting it's bilingual context. Write the persona in English (it's an internal coordination document); the actual chat output mirrors the learner's language as always.
- ❌ Storing factual recall ("answered Q3 correctly"). That's `lesson_answers` / `concept_mastery`.
- ❌ Storing emotional inferences as fact. Phrase as `"appears to..."` / `"tends to..."`, not `"hates..."`.

## Example flow

A learner explicitly says "I learn way better when you give me a real-world example first":

1. The Tutor recognises this is a stable HOW preference, not a one-off.
2. The Tutor calls:
   ```
   PATCH /api/agent-memory/persona
   { "section": "How they like explanations",
     "line": "Asks for a real-world example before the rule." }
   ```
3. From the next turn onward — INCLUDING in chats with the Mentor, Coach, and Q&A Explainer — every agent's prompt contains:
   ```
   ## What I know about this learner (shared persona)
   ...
   ## How they like explanations
   - Asks for a real-world example before the rule.
   ...
   ```
4. The Mentor in a later session opens with a real-world example before the rule — without the learner having to say so again.

That's the whole point.
