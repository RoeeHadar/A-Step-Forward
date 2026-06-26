---
name: agent-skill-notes
description: Per-(learner, agent) cumulative, additive scratchpad. Each learner-facing agent has its OWN private notes about THIS learner that no other agent reads. How to read, how to write, when to consolidate. Pair with `skills/learner-persona/SKILL.md` (the shared persona) and `skills/dreaming-and-consolidation/SKILL.md` (the cleanup pass).
---

# Agent Skill Notes

## Purpose

Each runtime agent (tutor, mentor, coach, reviewer, qa_explainer, note_taker, accessibility, engagement) gets a **private**, **additive**, **per-learner** scratchpad. Think of it as the agent's own field notes about THIS learner — strategies it tried that worked, open questions it didn't get to, micro-preferences that fit the agent's role but don't belong in the shared persona.

These are the agent's **skills dedicated to this user** — they accumulate over time, the agent reads them on every turn (top-K, importance-sorted), and the dreaming pass prunes them when they get cluttered.

## What lives here

| Kind            | Example                                                                                            |
| --------------- | -------------------------------------------------------------------------------------------------- |
| `observation`   | "Switches to English when stressed."                                                                |
| `preference`    | "Prefers 'show me first, ask me later' over Socratic openings."                                    |
| `strategy`      | "When stuck on derivatives, anchoring on the velocity = slope analogy works in 4/5 attempts."     |
| `open_question` | "Hasn't tried any optimization problems yet — worth probing next session."                          |
| `misconception` | "Conflates congruent and similar — verify before any geometry session."                            |
| `win`           | "First derivation done without a hint on 2026-06-25 — celebrate next return."                      |
| `plan`          | "Next session: revisit `area_scale_factor` after one warm-up on prerequisite `area_basics`."        |

Each kind is just a tag; the renderer doesn't branch on it. The agent decides; the chat route reads.

## What does NOT belong

- ❌ Anything other agents need too — that's `learner_persona` (separate skill).
- ❌ Mastery deltas — that's `concept_mastery` / `skill_practice` (auto-tracked).
- ❌ Long verbatim quotes — clip to ≤ 600 chars (hard cap).
- ❌ Notes you can't justify with "I'll still use this in 2 weeks".

## Schema

```sql
CREATE TABLE learner_agent_notes (
  id                 UUID PRIMARY KEY,
  learner_id         TEXT NOT NULL,
  agent              TEXT NOT NULL,          -- canonical agent name
  kind               TEXT NOT NULL DEFAULT 'observation',
  content            TEXT NOT NULL,          -- 600 char hard-cap
  importance         INT  NOT NULL DEFAULT 3,-- 1..5
  related_concept_id TEXT,                   -- optional
  source_turn_id     UUID,                   -- chat_turns.id, optional
  superseded_by      UUID REFERENCES learner_agent_notes(id),
  archived_at        TIMESTAMPTZ,
  last_referenced_at TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL
);
```

Indexes:
- `(learner_id, agent, created_at DESC)` for "recent K notes".
- `(learner_id, agent, importance DESC, created_at DESC)` for "top K by importance".

Both indexes are `WHERE archived_at IS NULL AND superseded_by IS NULL` — so they only see live notes.

## API

```ts
GET    /api/agent-memory/notes?agent=<name>&limit=<n>
  → { notes: [ { id, kind, content, importance, related_concept_id, created_at } ] }

POST   /api/agent-memory/notes
  body: {
    agent: <name>,              // canonical name, validated by agentNameSchema
    content: string,            // hard-capped to 600 chars
    importance?: 1..5,          // default 3
    kind?: 'observation' | 'preference' | 'strategy'
         | 'open_question' | 'misconception' | 'win' | 'plan',
    related_concept_id?: string|null,
    source_turn_id?: uuid|null
  }
  → { id }

DELETE /api/agent-memory/notes/<id>          // archive (soft-delete)
PATCH  /api/agent-memory/notes/<id> { by }   // mark superseded by <by>

POST   /api/agent-memory/dream
  body: { agent?: <name> }    // omit to run for all agents the learner has notes for
  → { archived, superseded, agents_processed }
```

The dreaming endpoint is **deterministic**: cap-and-archive lowest-importance / oldest, plus token-set Jaccard de-dupe (≥ 0.6 → supersede older by newer). The heavy LLM-driven version lives with the Memory Steward and runs nightly.

## How the chat route reads notes

On every turn, the chat route (`apps/web/src/app/api/chat/route.ts`) loads
**this agent's** top-6 notes (importance desc, created_at desc) and injects
them as:

```
## My private notes on this learner (agent: <you>)
These are your past observations, preferences you've recorded, and strategies that worked.
- (preference, importance 4) Prefers worked example first.
- (strategy, importance 4) [concept:derivatives_intro] velocity = slope analogy worked.
- (open_question, importance 3) Hasn't tried optimization problems yet.
…
```

Limit is 6 by default to leave room for the rest of the context. Agents
can read more on demand via the GET endpoint.

## When to write

- **After a successful pivot.** Strategy X worked where strategy Y failed → write a `strategy` note (importance 4).
- **When you explicitly noticed a HOW preference** that's specific to your role (e.g. for Coach: "responds better to time-boxed drills than open-ended practice").
- **When you parked an open question** ("we'll revisit polar coords next session") — write as `plan`.
- **When you observed a misconception you want to verify next time** — write as `misconception` with `related_concept_id` set.
- **When the learner had a real win** — write as `win` so future sessions can reference it ("last time you nailed the first derivation without a hint…").

## When NOT to write

- After every turn. The list is for top-K with `importance`; flooding it with `importance: 3` noise just gets pruned.
- For an observation that belongs in the shared `learner_persona` (other agents need it too) — write that instead.
- Things `concept_mastery` already tracks ("did Q3 correctly").

## Importance scale

| Importance | Meaning                                                                          |
| ---------- | -------------------------------------------------------------------------------- |
| 5          | Crucial. Read this every session ("MAJOR misconception", "anxiety-triggered topic"). |
| 4          | Strong. Likely-useful in the next 2-3 sessions.                                 |
| 3 (default)| Worth keeping for now; the dreaming pass may prune.                            |
| 2          | Speculative. Will get archived if unrefenced for ~30d.                          |
| 1          | Trivia. Don't bother unless you're really sure.                                  |

## Pitfalls

- ❌ Writing notes about other agents (or notes that mention another agent's role explicitly). Each agent only sees its OWN notes.
- ❌ Storing PII or schools / locations — clamp + redact at the source.
- ❌ Importance inflation. Reserve `importance: 5` for true must-read items.
- ❌ Forgetting `related_concept_id` for concept-specific notes — those are gold for the Progress Analyzer if/when it picks up cross-agent notes.
- ❌ Long, paragraph-style notes. 1–2 sentences max. The chat route's context budget is finite.

## Example flow

A Tutor session:

1. Learner consistently solves geometry problems wrong because they confuse SSS and SSA.
2. Tutor catches it three times in one session, finally lands the fix.
3. Tutor calls:
   ```json
   POST /api/agent-memory/notes
   {
     "agent": "tutor",
     "kind": "misconception",
     "content": "Confuses SSS vs SSA — needs explicit included-angle distinction first.",
     "importance": 4,
     "related_concept_id": "triangles_congruence"
   }
   ```
4. Three sessions later, the same Tutor opens a geometry chat. Its system prompt now contains:
   ```
   ## My private notes on this learner (agent: tutor)
   - (misconception, importance 4) [concept:triangles_congruence] Confuses SSS vs SSA — needs explicit included-angle distinction first.
   ```
5. The Tutor opens the session by checking the distinction before diving in.

That's the loop.
