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
`buildContextPrompt(userId, agent, message)` builds the system message:

1. Base persona (`AGENT_PERSONAS[agent]`).
2. Learner profile snapshot (goal, grade, subjects, hours/week, next test date,
   final goal date, mental_state).
3. Top weak + strong concepts from `concept_mastery`.
4. KG concepts whose `id`, English name, or Hebrew name appear in the user's
   message — limited to 3 to keep the prompt tight.
5. If `mental_state.anxiety >= 7`, an extra instruction telling the model to
   soften tone and avoid time pressure language.

## Adding a new agent
1. Add the persona to `AGENT_PERSONAS` in `apps/web/src/app/api/chat/route.ts`.
2. Add the agent to `agentNameSchema` in `packages/schemas/ts/agents.ts`.
3. Add a UI tile / page under `apps/web/src/app/(app)/app/chat/[agent]/page.tsx`.
4. Update the agent switcher pill list in the same page.

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
