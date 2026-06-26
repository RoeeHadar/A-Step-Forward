# Phase 7 — Real `/app` stats + remove Lessons + AI Custom Quiz

Reading list before any work: `PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md`, plus
the two skill docs that bound this slice:

- `skills/build-custom-quiz/SKILL.md`
- `skills/neon-direct-route/SKILL.md`

This brief closes three user-visible bugs / requests:

1. The `/app` dashboard was showing fabricated activity ("Streak 7 / Lessons
   completed 12 / Level 3 / Introduction to Fractions") for brand-new
   learners. Streak was also not advancing for real learners.
2. The Lessons section was empty (everything "coming soon"); the user wanted
   it hidden from the sidebar but the route kept alive with a brief
   explanation of what's planned.
3. A new Quiz section was requested in the sidebar where a learner can
   self-test on **chosen kind-mix (open / closed / mixed)**, **chosen time
   budget**, and **optionally chosen topics** — with the AI generating new,
   fit-to-purpose questions based on the learner's mastery + profile.

## 1. Real `/app` dashboard stats

**Code**

- `apps/web/src/lib/neon-db.ts`:
  - New `getDashboardSnapshot(learnerId)` returns `{ stats, recent_lessons,
    mastery_summary }`. `stats.streak_days` delegates to `getLearnerStreak`.
    `lessons_completed` = count of `concept_mastery.score >= 0.7`. `level`
    = `1 + floor(completed/3) + floor(atoms_practiced/12)` — stays at 1 for
    brand-new learners and grows as real work happens. `recent_lessons` and
    `mastery_summary` are joined with the in-process KG for bilingual names
    and with `lessons` for the authored-lesson id + est_minutes.
  - Extended `LessonMeta` (and its query) to include `id`, `title_en`,
    `title_he`, `est_minutes` so the dashboard can render real recent-lesson
    tiles without a second round-trip. Backwards-compatible additive change.
- `apps/web/src/app/(app)/app/page.tsx` — calls `getDashboardSnapshot`
  directly (no Render call), passes the snapshot to `DashboardContent`. No
  hardcoded stat defaults. Brand-new learners get an `emptySnapshot()`.
- `apps/web/src/components/dashboard-content.tsx` — rewritten to accept a
  `DashboardSnapshot` instead of a `LearnerDashboard` mock; every number
  on screen now comes from Neon. Renders bilingual concept names via
  `name_he`, deep-links to `/app/lessons/l/<id>` when the authored lesson
  exists or `/learn/<subject>` otherwise.
- `apps/web/src/lib/data.ts` — `MOCK_DASHBOARD` and `MOCK_PROGRESS` are now
  empty fallbacks. Any legacy code path that still calls `fetchDashboard()`
  / `fetchProgress()` gets the same empty-state semantics; nothing in the
  app can render fake fractions anymore.

**Behaviour**

- Brand-new learner: Streak 0, Lessons completed 0, Level 1, "No lessons
  yet", "No mastery yet". (Before: 7 / 12 / 3 + fake "Introduction to
  Fractions" / "Fractions 72%".)
- After answering a few diagnostic / lesson questions: the streak advances
  because `recordDiagnosticAnswer` / `recordLessonAnswer` already update
  `concept_mastery.last_activity`, and `getLearnerStreak` unions
  `chat_turns` + `concept_mastery.last_activity` + `skill_practice.last_practiced`.

## 2. Lessons hidden + placeholder

**Code**

- `apps/web/src/components/app-sidebar.tsx` — removed the Lessons nav item;
  added a Quiz item pointing to `/app/quiz`.
- `apps/web/src/i18n/messages.ts` — new `nav.quiz` label in EN + HE.
- `apps/web/src/app/(app)/app/lessons/page.tsx` — rewritten as a
  bilingual "video lectures coming soon" placeholder. Explains what the
  section will host (video lectures + interactive synced practice +
  timestamps) and CTA's to `/app/quiz` and `/app/chat/tutor`.

## 3. AI Custom Quiz

**Code**

- `apps/web/src/lib/quiz-builder.ts` — server-only library that:
  1. Picks concepts (user-chosen ➜ weakest-mastery ➜ subject-bootstrap).
  2. Sizes question count from the time budget (closed ~1.2 min, mixed ~2
     min, open ~3.5 min; clamped to [3, 20]).
  3. Calls Groq (Llama 3.3 70B with 3.1 8B fallback) with a strict
     bilingual JSON contract, validates each item against a per-kind
     schema, drops anything malformed.
- `apps/web/src/app/api/quiz/custom/route.ts` — authed POST endpoint.
  503 if Groq is unavailable / output unusable.
- `apps/web/src/app/(app)/app/quiz/page.tsx` — server page that ships the
  KG concept list (grouped by subject) to the client.
- `apps/web/src/components/quiz-page-client.tsx` — single-file bilingual UI
  with three phases: **builder** (kind + time + topics) ➜ **running**
  (per-kind question UI + countdown timer + KaTeX math) ➜ **results**
  (overall score, per-concept breakdown, per-question explanation +
  correct answer).

**Why ephemeral**

The quiz envelope is intentionally **not persisted** as a lesson — it's a
fit-to-purpose mini-assessment owned by the client. Per-item answers are
still posted to `/api/lesson/answer` (with `ephemeral: true`) so the
mastery / skill-practice pipeline still sees the practice and the
planner can react to it.

## 4. Skills + indices

- New `skills/build-custom-quiz/SKILL.md` — full contract, picking
  rules, sizing table, validation rules, pitfalls.
- `AGENTS.md` cross-cutting skills table now lists the new skill with a
  one-liner explaining when to use it (and when not to — durable question
  authoring still goes through `author-question-bank`).

## Acceptance criteria

- [x] `/app` shows real Streak / Lessons completed / Level / Recent lessons
      / Mastery for the authenticated learner; brand-new learners see zeros
      + empty states, not fake fractions.
- [x] Sidebar no longer shows Lessons; instead shows Quiz; both EN + HE.
- [x] `/app/lessons` renders a bilingual "video lectures coming soon"
      placeholder explaining the future and CTAs to the Quiz / Tutor.
- [x] `/app/quiz` renders a bilingual builder form with kind-mix radio,
      time-budget input + quick-picks, topic multi-select grouped by subject.
- [x] `POST /api/quiz/custom` returns a validated envelope or 503; UI shows
      a clear retry CTA on 503.
- [x] Quiz runner UI supports all five kinds (mcq, true_false, numeric,
      short_answer, open) bilingually with a countdown timer; results
      screen shows score + per-concept breakdown + per-question
      explanations.
- [x] No remaining references to `MOCK_DASHBOARD` / `MOCK_PROGRESS` with
      fake fractions anywhere in the app.

## Out of scope

- Persisting custom quizzes to a new `quiz_sessions` table. Today they
  live only in client component state; refreshing the page mid-quiz throws
  the envelope away (by design).
- An "AI-graded open question" pass on the results screen. Today the open
  kinds use a 3-way learner self-assessment (correct / partial / wrong);
  full LLM-graded rubrics can be added later behind a feature flag.
- Educator-facing custom quiz authoring. Today only the learner can build
  one for themselves through `/app/quiz`; an educator-mode entry point is
  in the backlog.
