# Phase 5 — Bilingual diagnostic + per-learner shared persona + per-agent private notes + streak surface

Owner: Coordinator
Status: Shipped (round 9)

## What changed

### 1. Bilingual diagnostic quiz

Up to round 8 the starting diagnostic for new learners was English-only because the seeder only authored EN stems / options / explanations. Israeli learners — who hit `/diagnostic` immediately after sign-up — saw English as their first contact with the platform, even though every authored lesson is fully bilingual.

- **Migration 0015** adds `diagnostic_items.stem_he`, `options_he`, `explanation_he` (nullable JSONB / TEXT). EN columns stay primary for backwards compat; the UI falls back to EN if the HE columns are null.
- **`scripts/seed_diagnostic_items.py`** now emits HE alongside EN for every (concept, difficulty) template, using each concept's `name_he` from the KG YAML.
- **`scripts/backfill-diagnostic-he.mjs`** populates HE columns on already-seeded rows in one pass (idempotent; `--force` to re-translate, `--dry-run` to preview). Use after migrating prod.
- **`apps/web/src/app/diagnostic/page.tsx`** reads `useLanguagePreference()` (default `he`), passes `dir="rtl"` + `lang="he"`, switches stems / options / aria labels / button copy through a `STR.he` / `STR.en` bundle, and renders the HE stem when available. Includes an inline `EN ↔ עב` toggle in the progress strip.
- **`fetchDiagnosticItems` / `itemToQuestion`** in `apps/web/src/lib/neon-db.ts` now return both languages so the client can switch without an extra round-trip.

### 2. Two new authoring skills for agents

The user flagged that questions are too narrow and theoretical explanations are too thin. Two skills now formalise the patterns:

- **`skills/author-question-bank/SKILL.md`** — how any agent (Assessment Generator, Tutor, Coach, Content Curator) generates +N questions on a concept that fit the existing 10-kind schema, the bilingual contract, and the `skill_atoms` planner contract. Covers coverage targets (≥ 12 questions / lesson; kind + difficulty mix; ≥ 1 question per atom), author-mode workflow (PR + re-seed), live-mode workflow (Coach drills), the quality bar, and suggested AI prompts.
- **`skills/expand-lesson-theory/SKILL.md`** — how to add MORE `worked_example`, `pitfalls`, `why_matters` sections to an authored lesson without breaking the schema. Includes the 5 canonical section kinds, the section shape, three recipes (higher-difficulty worked example; observed-misconception pitfall; cross-subject `why_matters` bridge), explicit boundary with `agent_hints` (DO NOT touch from this skill — pair with `author-lesson` if you need a new hint), and the re-seed + verify loop.

### 3. CLAUDE.md-style learner persona + per-agent private notes

The user's third ask was about giving every agent BOTH a personal scratchpad for the user AND a shared memory about the learner / theoretical database / their own role / dreaming. The shared theoretical database (`buildAgentBaseline`) and per-agent role (`getAgentPersona`) were already in place from round 8. Round 9 adds the two missing pieces:

- **Shared learner persona** (`learner_profiles.learner_persona TEXT` + `learner_persona_updated_at`). Free-form CLAUDE.md-style markdown summary of HOW the learner thinks, talks, and learns. Every agent reads it on every turn via the chat route, injected as `## What I know about this learner (shared persona)`. Documented in `skills/learner-persona/SKILL.md`.
- **Per-(learner, agent) private notes** (`learner_agent_notes` table). Each agent has its own private scratchpad about THIS learner that no other agent reads. The chat route loads the top-6 by importance/recency on every turn and injects them as `## My private notes on this learner (agent: <you>)`. Documented in `skills/agent-skill-notes/SKILL.md`.
- **API endpoints**:
  - `GET / POST / PATCH /api/agent-memory/persona` — read, full-replace, append-line-under-section.
  - `GET / POST /api/agent-memory/notes` — list + append note.
  - `DELETE / PATCH /api/agent-memory/notes/<id>` — archive / supersede.
  - `POST /api/agent-memory/dream` — lightweight deterministic consolidation (cap-and-archive + Jaccard dedupe). Heavy LLM consolidation stays with the Memory Steward.
- All endpoints are scoped to the authenticated Clerk `userId`; you cannot read another learner's data. Storage is Neon, keyed by `userId` — same identity bucket as the user themselves.
- **`apps/web/src/lib/agent-baseline.ts`** now documents the two memory channels under "Per-turn context the runtime already gives you" + "Memory you can write back", so every agent knows the channels exist on turn one (even a brand-new learner's chat).
- **`apps/web/src/app/api/chat/route.ts`** now loads `persona` + `agentNotes` in parallel with the existing profile / mastery / chat-turns fetch, and injects the two new blocks between profile and mastery.

### 4. Streak + recent-activity surface on `/dashboard`

The user asked for the website to "remember" what learners did — streaks, weekly plan, last quiz. The weekly plan UI (`LearningPlanDashboard`) was already shipped; what was missing was streaks + recent activity.

- **`getLearnerStreak(learnerId)`** unions every "something happened" signal (chat turns, lesson answers, quiz responses, mastery activity) into a single set of active days and computes current / longest / active-30 in one SQL query.
- **`getRecentActivity(learnerId, limit)`** returns the last N actions across chat / lesson / quiz with kind + agent + concept_id + detail + timestamp.
- **`apps/web/src/components/learner-streak-card.tsx`** — bilingual card (default HE) shown at the top of `/dashboard`. Three stat tiles (current / longest / active days last 30) + a list of recent actions with relative-time stamps.

## Files touched

```
infra/alembic/versions/0015_learner_persona_and_agent_notes.py          [new]
services/diagnostic/diagnostic_service/stores/models.py                 [+he columns]
scripts/seed_diagnostic_items.py                                        [+he template]
scripts/backfill-diagnostic-he.mjs                                      [new]
apps/web/src/lib/neon-db.ts                                             [bilingual diag + persona + notes + streak]
apps/web/src/lib/agent-baseline.ts                                      [+ memory channels]
apps/web/src/app/api/chat/route.ts                                      [+ persona + notes injection]
apps/web/src/app/api/agent-memory/persona/route.ts                      [new]
apps/web/src/app/api/agent-memory/notes/route.ts                        [new]
apps/web/src/app/api/agent-memory/notes/[id]/route.ts                   [new]
apps/web/src/app/api/agent-memory/dream/route.ts                        [new]
apps/web/src/app/diagnostic/page.tsx                                    [bilingual UI + lang toggle]
apps/web/src/app/dashboard/page.tsx                                     [+ streak card]
apps/web/src/components/learner-streak-card.tsx                         [new]
skills/author-question-bank/SKILL.md                                    [new]
skills/expand-lesson-theory/SKILL.md                                    [new]
skills/learner-persona/SKILL.md                                         [new]
skills/agent-skill-notes/SKILL.md                                       [new]
skills/dreaming-and-consolidation/SKILL.md                              [+ web runtime pass]
skills/chat-memory-context/SKILL.md                                     [+ 9-layer composition]
AGENTS.md                                                               [+ memory layer table + new skills]
```

## Deployment / verify checklist

1. **Migrate Neon**: `gh workflow run "Migrate Neon"` (runs through to head, applies 0015).
2. **Backfill HE diagnostic columns**: `DATABASE_URL=... node scripts/backfill-diagnostic-he.mjs`. Verify with a single `SELECT id, stem_he IS NOT NULL FROM diagnostic_items LIMIT 5`.
3. **Deploy**: `Deploy Web (Vercel)` workflow runs on push; otherwise `vercel --prod` from `apps/web`.
4. **Manual probes**:
   - `/diagnostic` → first question stem renders in Hebrew, RTL paragraph, math expressions are LTR. Toggle EN, then back to עב; selection should persist across reloads.
   - `POST /api/agent-memory/persona { text: "## How they talk\\n- Casual Hebrew." }` → 200; `GET` returns the same body.
   - `POST /api/agent-memory/notes { agent: "tutor", content: "Likes worked examples first." }` → returns `{ id }`; `GET /api/agent-memory/notes?agent=tutor` returns the note.
   - `/dashboard` → streak card renders bilingually (HE default), shows current 0 / longest 0 / 0/30 for a new account.
5. **Smoke chat**: `POST /api/chat { agent: "tutor", message: "מה כדאי שאלמד עכשיו?" }` → response system prompt (visible in server logs in dev) includes both `## What I know about this learner` and `## My private notes on this learner (agent: tutor)` blocks after writing the persona + note above.

## Follow-ups (not shipped this round)

- **Heavy LLM consolidation** — schedule the Memory Steward nightly pass that promotes durable notes into the shared persona. Currently only the deterministic web pass exists.
- **Persona UI** — a `/settings/persona` page where the learner can view (and optionally redact) the shared persona. The API is in; the UI page isn't.
- **Author bulk +N questions** — the skill is in; actual content authoring against the 69 remaining lessons is the next content sprint.
- **Bilingual quiz responses on /dashboard** — the LearningPlanDashboard itself is still partially EN. Targeted i18n pass when we next touch it.
- **Activity heatmap** — the streak card currently shows totals; a 30-day grid would help spot patterns.
- **Per-week "what you did this week" recap** — partial data is in `getRecentActivity`; needs a weekly aggregator and a digest UI.
