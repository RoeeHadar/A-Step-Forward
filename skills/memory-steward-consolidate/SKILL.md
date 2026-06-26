---
name: memory-steward-consolidate
description: Heavy, LLM-driven per-learner consolidation of per-(learner, agent) notes into the shared persona. Read BEFORE editing the consolidate endpoint, the cron sweep, or the rebuild button.
---

# Memory Steward — heavy consolidation pass

## Purpose

Keep the learner's shared **persona** durable, compact, and free of clutter.
Every chat turn injects:

- `learner_profiles.learner_persona` — shared across all agents
- `learner_agent_notes` (top 8 per agent) — private scratchpad per agent

Agents append notes liberally. Without a consolidation pass:

- The private scratchpads grow until the (already capped) top-K becomes stale.
- High-signal observations live forever in note form and never reach
  the shared persona — so other agents never benefit from them.

This skill documents the **heavy** pass that fixes both: it summarises
all live notes into the persona body and archives the ones that have
been "promoted".

## Pieces

| Piece | Path |
| --- | --- |
| Library | `apps/web/src/lib/persona-consolidator.ts` |
| Per-user endpoint | `apps/web/src/app/api/agent-memory/consolidate/route.ts` |
| Cron sweep | `apps/web/src/app/api/cron/consolidate-memory/route.ts` |
| Vercel cron entry | `apps/web/vercel.json` → `crons[]` |
| GitHub backstop cron | `.github/workflows/cron-consolidate-memory.yml` |
| UI button | `apps/web/src/components/persona-editor.tsx` (`Rebuild from notes`) |

## Contract — `consolidateLearnerMemory(learnerId, { force? })`

1. Loads `getLearnerPersona(learnerId)` and up to 80 live notes (importance desc).
2. If `notes.length < 6` and `force` is false, returns `{ ran: false, reason: 'notes_below_threshold' }`.
3. Otherwise calls Groq (`llama-3.3-70b-versatile` → fallback `llama-3.1-8b-instant`) with a fixed system prompt that mandates:
   - JSON-only output: `{ persona, promoted_ids[], notes? }`
   - persona ≤ 4000 chars
   - markdown H2 sections (recommended: `How they talk`, `How they like explanations`, `Triggers and preferences`, `Recent durable observations`)
   - **no PII** (names, schools, emails, phones, addresses dropped)
   - HOW-related observations only; never copies `concept_mastery` content
   - persona text written in **English** (it's an internal coordination doc; agents mirror the learner's language in chat anyway)
4. Writes the consolidated persona via `setLearnerPersona`.
5. Archives each note id in `promoted_ids` (intersected with the live set for hallucination defence) via `supersedeAgentNote(id, null)`.

Returns: `{ ran, reason?, persona_chars_before, persona_chars_after, notes_considered, notes_archived, model? }`.

## When to call

- **Settings page button** — `Rebuild from notes` in `/settings/persona`. Calls
  `POST /api/agent-memory/consolidate { force: false }`. Surfaces the
  result inline.
- **Weekly cron** — `Sunday 03:00 UTC` via two paths (whichever is
  available in your tier):
  - Vercel cron: `apps/web/vercel.json` → `/api/cron/consolidate-memory?limit=25`
  - GitHub Actions: `.github/workflows/cron-consolidate-memory.yml`
- **Educator/admin tooling** — POST to either endpoint with the right auth.
- **Never** on the request path — this is a 20-second LLM round trip.

## CRON_SECRET

The cron route refuses to run without `process.env.CRON_SECRET`. Vercel
auto-attaches `Authorization: Bearer <secret>` to cron invocations; the
GitHub workflow sends `x-cron-secret: <secret>`. Both headers are
accepted.

## What the heavy pass deliberately does NOT do

- Touch `concept_mastery` or `skill_practice` (those are owned by the
  lesson/quiz answer paths).
- Run the deterministic dedupe/cap pass — that's `/api/agent-memory/dream`
  and stays separately callable (it's cheap and idempotent).
- Project into the Knowledge Graph (KG projection lives in the full
  Memory Steward service in `services/memory/`).

## Pitfalls

- **Don't lower `MIN_NOTES_TO_CONSOLIDATE`** to 0 for the cron; you'll
  burn Groq tokens on learners with nothing meaningful to consolidate.
- **Don't drop the "JSON only" instruction** — `response_format: json_object`
  helps but the model still occasionally leaks markdown around the JSON.
  Parse with try/catch and fall through to the next model on failure.
- **Don't accept `promoted_ids` blindly** — always intersect with the
  live note ids fetched before the call. Models hallucinate ids.
- **Don't run more than `MAX_LIMIT=100` learners per invocation** —
  Vercel function timeouts will bite. Re-invoke the workqueue instead.
- **Don't echo the persona body into logs** — it's user content.

## Verification

After deploy:

```
curl -sS -X POST $BASE/api/agent-memory/consolidate
  # expect: 401 (no Clerk session)

curl -sS -X POST -H "x-cron-secret: $CRON_SECRET" \
  "$BASE/api/cron/consolidate-memory?limit=1"
  # expect: { candidates, runs_completed, notes_archived, per_learner: [...] }
```
