---
name: chat-memory-context
description: >
  How chat persistence + per-agent memory + KG/profile context injection works
  in this codebase. Read before changing the chat route, adding a new agent, or
  modifying what gets persisted on a turn.
---

# Chat memory + context

## Architecture in one paragraph

`/api/chat` (apps/web) is the single entry point for all learner chat. Every
turn it (a) records the user message to `chat_turns`, (b) tries the Render
backend with a 90-second timeout, (c) on failure falls back to a direct Groq
call enriched with the learner's profile + recent memory + relevant KG concepts,
and (d) records the assistant message to `chat_turns` after the stream closes.

## chat_turns schema
```
id          UUID PRIMARY KEY
learner_id  TEXT       -- Clerk userId
agent       TEXT       -- 'tutor' | 'mentor' | 'coach' | ...
role        TEXT       -- 'user' | 'assistant'
content     TEXT
session_id  TEXT NULL  -- optional grouping
created_at  TIMESTAMPTZ
```
Indexed on `(learner_id, created_at DESC)` and `(session_id, created_at)`.

## How memory is loaded
`fetchRecentChatTurns(learnerId, agent, limit=10)` returns the last 10 turns
**for that agent only**, oldest first. The chat route appends them to the
system message and feeds them straight to Groq as `messages`.

Memory is **per-agent** on purpose — switching from Tutor to Mentor gives the
learner a fresh start with that personality.

## How profile / mastery / KG context gets injected
`buildContextPrompt(userId, agent, message)` builds the system message in this
exact order — each layer can be absent independently:

1. **Shared agent baseline** (`apps/web/src/lib/agent-baseline.ts` →
   `buildAgentBaseline()`). Corpus stats, KG dimensions, agent network
   roster, universal rules (bilingual HE-default, math LTR, no external
   links, brand-new-learner protocol). Same for every agent.
2. **Long-form agent persona** (`apps/web/src/lib/agent-prompts.ts` →
   `getAgentPersona(agent)`). Per-agent tools allowlist, style, hand-off
   rules, refusal/safety. Versioned in-file.
3. **Brand-new-learner cue** if `getLearnerProfile()` returned null —
   tells the agent to invite the learner to `/onboarding` and NOT to
   improvise a curriculum.
4. **Learner profile snapshot** (goal, grade, subjects, hours/week, next
   test date, final goal date, mental_state).
5. **`## What I know about this learner (shared persona)`** — the
   CLAUDE.md-style learner persona from `learner_profiles.learner_persona`.
   Read-mostly across every agent. Updated by agents via
   `/api/agent-memory/persona`. See `skills/learner-persona/SKILL.md`.
6. **`## My private notes on this learner (agent: <name>)`** — the top-K
   notes from `learner_agent_notes` for THIS (learner, agent). Never
   crosses agents. Updated by the agent itself via
   `/api/agent-memory/notes`. See `skills/agent-skill-notes/SKILL.md`.
7. **Top weak + strong concepts** from `concept_mastery`.
8. **Relevant curriculum context** — KG concepts whose `id`, English
   name, or Hebrew name appear in the user's message (cap 3).
9. **Lesson-level agent_hints** (tutor / coach / qa_explainer) — key
   insights, pacing hints, common misconceptions (triggered by detect
   phrases in the learner's message), diagnostic moves, skill atoms
   unlocked.
10. **Learning-plan snapshot** (tutor / coach / qa_explainer /
   curriculum_designer / progress_analyzer) — `buildLearningPlan()`
   walked from the most-relevant concept. Ordered `path[]` +
   `blocking_atoms[]`.
11. **Mental_state.anxiety ≥ 7** → extra instruction to soften tone.

Order matters: the baseline gives universal context, the persona narrows
to the agent's role, then the durable memory layers (shared persona +
private notes) personalise it to this learner, and finally the per-turn
signals fire when relevant. Never skip a layer — fall back to placeholders
if a helper throws.

## Per-(learner, agent) cumulative memory at a glance

| Layer                     | Scope                 | Table                       | Writer            | Reader                                      | Skill                           |
| ------------------------- | --------------------- | --------------------------- | ----------------- | ------------------------------------------- | ------------------------------- |
| Shared learner persona    | per-learner           | `learner_profiles.learner_persona` | Any agent (sparingly) + Memory Steward | Every agent on every turn | `skills/learner-persona/SKILL.md` |
| Agent private notes       | per-(learner, agent)  | `learner_agent_notes`       | Owning agent      | Owning agent (top-K, importance-sorted)     | `skills/agent-skill-notes/SKILL.md` |
| Streamed chat turns       | per-(learner, agent)  | `chat_turns`                | Chat route        | Owning agent (last N)                       | This skill                      |
| Mastery                   | per-(learner, concept)| `concept_mastery`           | Grader + lesson/answer routes | Everyone via context              | `skills/use-learning-plan/SKILL.md` |
| Atom mastery              | per-(learner, atom)   | `skill_practice`            | Lesson/answer route | Learning planner                          | `skills/cross-subject-kg/SKILL.md` |

Memory is **per-agent** for chat turns + notes on purpose — switching
from Tutor to Mentor gives a fresh start with that personality. The
shared persona is the only learner-level layer that follows the user
across agents.

## Adding a new agent
1. Add the long-form persona to `AGENT_PROMPTS` in
   `apps/web/src/lib/agent-prompts.ts` (include tools list, style, hand-off
   rules, refusal/safety, output format).
2. Also add a one-line fallback to `AGENT_PERSONAS` in
   `apps/web/src/app/api/chat/route.ts` (used only if `agent-prompts.ts`
   fails to load).
3. Author / update the matching `prompts/<agent>/v1.md` for sub-agent /
   human readers — must stay in sync with the runtime version.
4. Add the agent to `agentNameSchema` in `packages/schemas/ts/agents.ts`.
5. Add a UI tile / page under `apps/web/src/app/(app)/app/chat/[agent]/page.tsx`.
6. Update the agent switcher pill list in the same page.

No schema changes needed — `chat_turns.agent` is just `TEXT`.

## Adding a new context source
If you want, e.g., recent dashboard activity or recent quiz scores in the
system prompt, add a helper to `neon-db.ts`, call it from `buildContextPrompt`,
and append a new section to the `context` string. Keep the prompt under
~2k tokens — trim aggressively.

## Things to avoid
- **Do not** store assistant tokens before the stream completes — you will
  truncate on early disconnects. The route currently accumulates in
  `assistantBuffer` and writes once in the `close()` handler.
- **Do not** trust the client-provided `messages` array as long-term memory —
  it is per-conversation and will be lost on refresh. Always rebuild from
  `chat_turns` server-side.
- **Do not** pull memory across agents. Each persona has its own thread.
