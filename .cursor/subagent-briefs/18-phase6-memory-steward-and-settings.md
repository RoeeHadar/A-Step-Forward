# Phase 6 — Memory Steward (heavy), persona settings, bulk-q, dashboard recap

Reading list before any work: `PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md`, plus
the three skill docs that bound this slice:

- `skills/memory-steward-consolidate/SKILL.md`
- `skills/learner-persona/SKILL.md`
- `skills/author-question-bank/SKILL.md`

This brief closes the four pending items from Phase 5
(`17-phase5-persona-and-agent-memory.md`):

## 1. Heavy LLM-driven persona consolidation

**Code**

- `apps/web/src/lib/persona-consolidator.ts` — pure library, Groq-backed:
  - `consolidateLearnerMemory(learnerId, { force? })` — 1 LLM round-trip per
    learner. Reads `learner_persona` + up to 80 live notes (importance desc).
    Returns `{ ran, reason?, persona_chars_before/after, notes_considered,
    notes_archived, model? }`.
  - `listLearnersWithLiveNotes()` — workqueue for the cron sweep.
- `apps/web/src/app/api/agent-memory/consolidate/route.ts` — `POST`, authed.
  Used by the `Rebuild from notes` button. 60 s `maxDuration`.
- `apps/web/src/app/api/cron/consolidate-memory/route.ts` — `GET` + `POST`,
  `CRON_SECRET`-gated. Iterates the workqueue up to `?limit=N` (default 25,
  cap 100) and runs the heavy pass per learner.

**Cron wiring**

- `apps/web/vercel.json` → `crons[]` runs `Sunday 03:00 UTC` against the
  cron route at limit=25.
- `.github/workflows/cron-consolidate-memory.yml` is the GitHub Actions
  backstop with the same schedule, callable from `workflow_dispatch`.
  Required secrets: `WEB_BASE_URL`, `CRON_SECRET`.

**LLM contract** (system prompt enforces — see `persona-consolidator.ts`):

- JSON-only output: `{ persona, promoted_ids[], notes? }`
- persona ≤ 4000 chars
- markdown H2 sections (recommended: `How they talk`, `How they like
  explanations`, `Triggers and preferences`, `Recent durable observations`)
- never include PII (names/schools/emails/phones/addresses)
- HOW the learner thinks/talks/learns — never copies `concept_mastery`
- only promotes notes whose content is actually present in the new persona

`promoted_ids` are intersected with the live ids before archiving as
hallucination defence.

## 2. `/settings/persona` UI

- `apps/web/src/app/settings/persona/page.tsx` — server component, gated by
  `ensureOnboarded`, loads the persona + per-agent note counts in parallel.
- `apps/web/src/components/persona-editor.tsx` — client component:
  - bilingual UI (`useLanguagePreference`, default `he`, RTL header)
  - markdown textarea (always LTR for the source, regardless of UI dir)
  - `Save` → `POST /api/agent-memory/persona`
  - `Rebuild from notes` → `POST /api/agent-memory/consolidate`, then
    re-fetches `GET /api/agent-memory/persona` to show the merged body.
  - per-agent note-count grid for the six learner-facing agents (tutor,
    mentor, coach, reviewer, qa_explainer, note_taker).

## 3. Bulk question generator

- `scripts/generate-bulk-questions.mjs` — Groq-backed authoring loop.
  CLI flags: `--target` (default 12), `--add`, `--limit`, `--only`,
  `--dry-run`. Enforces:
  - Mix of kinds (≥ 3 distinct in each batch)
  - At least one easy / medium / hard difficulty per batch
  - `skill_atoms` ⊆ lesson's `agent_hints.skill_atoms_unlocked`
  - Full bilingual EN + HE
  - No duplicate stems against existing questions
  - Schema validation matches `scripts/seed-lessons.mjs` exactly;
    invalid questions are dropped, not coerced.
- Wired into `.github/workflows/seed-db.yml` as the
  `generate-bulk-questions` target. Required secret: `GROQ_API_KEY`.
  After a run, review the diff, PR it, then re-run the
  `lessons-from-json` target to push the new questions to Neon.
- Documented in `skills/author-question-bank/SKILL.md` (Bulk-generation
  script section).

## 4. 30-day activity heatmap + this-week recap

- `apps/web/src/lib/neon-db.ts` adds:
  - `getDailyActivity(learnerId, days=30)` — generates a zero-filled series
    summing chat turns (user-side) + distinct concepts touched + distinct
    atoms practiced per day. UTC days, ordered oldest → newest.
  - `getWeeklyRecap(learnerId)` — current ISO week aggregates: chat turns,
    distinct concepts, distinct atoms, mastery-points sum, best day.
- `apps/web/src/components/activity-heatmap.tsx` — bilingual card. Renders a
  fixed 30-cell grid (`grid-cols-[repeat(30,minmax(0,1fr))]` on sm+; 15 cols
  below) coloured by 5-level intensity buckets. The grid is always LTR even
  in Hebrew UI (calendars read L→R in both languages here). A "This week"
  panel sits below with the four aggregates + best-day callout.
- `apps/web/src/app/dashboard/page.tsx` runs all five lookups in parallel and
  renders `LearnerStreakCard` → `ActivityHeatmap` → `LearningPlanDashboard`.

## Touched files (summary)

- `apps/web/src/lib/persona-consolidator.ts` (new)
- `apps/web/src/lib/neon-db.ts` (+`DailyActivity`, +`getDailyActivity`, +`WeeklyRecap`, +`getWeeklyRecap`)
- `apps/web/src/lib/agent-baseline.ts` (mentions heavy consolidate endpoint)
- `apps/web/src/app/api/agent-memory/consolidate/route.ts` (new)
- `apps/web/src/app/api/cron/consolidate-memory/route.ts` (new)
- `apps/web/src/app/settings/persona/page.tsx` (new)
- `apps/web/src/components/persona-editor.tsx` (new)
- `apps/web/src/components/activity-heatmap.tsx` (new)
- `apps/web/src/app/dashboard/page.tsx` (heatmap wired)
- `apps/web/vercel.json` (cron entry)
- `.github/workflows/cron-consolidate-memory.yml` (new)
- `.github/workflows/seed-db.yml` (+ `generate-bulk-questions` target)
- `scripts/generate-bulk-questions.mjs` (new)
- `skills/memory-steward-consolidate/SKILL.md` (new)
- `skills/dreaming-and-consolidation/SKILL.md` (link to heavy pass)
- `skills/author-question-bank/SKILL.md` (bulk-q script section)
- `AGENTS.md` (heavy consolidate + settings + cross-cutting skill row)

## Deployment / verification checklist

1. `pnpm --filter @asf/web build` on Vercel — should pass.
2. Set/refresh secrets on Vercel: `CRON_SECRET`.
3. Set/refresh secrets in GitHub repo: `CRON_SECRET`, `WEB_BASE_URL` (e.g.
   `https://a-step-forward-waij.vercel.app`), `GROQ_API_KEY` (for bulk-q).
4. Smoke tests against the production alias:

   ```
   # auth-gated → 401 expected (no Clerk session)
   curl -sS -X POST $BASE/api/agent-memory/consolidate

   # cron sweep → expect { candidates, runs_completed, notes_archived, per_learner }
   curl -sS -X POST -H "x-cron-secret: $CRON_SECRET" \
     "$BASE/api/cron/consolidate-memory?limit=1"

   # settings page renders
   curl -sS -o /dev/null -w '%{http_code}\n' $BASE/settings/persona
   ```

5. Open `/dashboard` as a real learner → confirm `LearnerStreakCard` →
   `ActivityHeatmap` → plan panel render in that order, all bilingual.
6. Open `/settings/persona` → confirm the textarea + `Save` + `Rebuild from
   notes` flow. With < 6 notes you should see "Skipped: notes_below_threshold".

## Pending follow-ups (later rounds)

- KG projection from consolidated persona events (Memory Steward → KG).
- Per-learner timezone for streak/heatmap day boundaries (currently UTC).
- Educator-facing read view of learner personas (RBAC `educator` only).
- Bulk-question generator running as a scheduled GitHub workflow instead of
  manual `workflow_dispatch`.
