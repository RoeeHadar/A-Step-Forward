# Coordinator Directive — Round 8 (2026-06-26)

Read `14-adaptive-learning-architecture.md` for the architectural vision and
`15-coordinator-directive.md` for Round 7's state.
This brief documents Phase 4 (cross-subject KG + learning plan + question
kinds + HE-default + math LTR) and the runtime-agent grounding work that
followed.

> **Supervisor note.** This was a large shipment across schema, backend,
> frontend, agents, and content. Read this whole brief before assigning any
> follow-up work. Do not regress what's here.

---

## What just shipped

### Schema (Alembic 0014)

- **`kg_edges`** — directed, weighted cross-concept relationships
  (`relation` ∈ `prereq|applies_to|generalizes|models|tooling_for`, `weight`).
  Used by the learning-plan walk.
- **`skill_atoms`** — first-class canonical skills (e.g. `area_scale_factor`,
  `free_body_diagram_force_sum`). Atom-level mastery is the new currency of
  the planner.
- **`lesson_skill_atoms`** — many-to-many `(lesson, atom, role)` where role
  is `teaches` or `exercises`. Auto-backfilled by `seed-lessons.mjs` from
  `agent_hints.skill_atoms_unlocked[]` (teaches) and per-question
  `skill_atoms[]` (exercises).
- **`lesson_questions.answer_payload JSONB`** — flexible payload for the new
  question kinds (was previously fixed to MCQ shape).

### Cross-subject KG

- **`apps/web/src/lib/kg-cross-edges.json`** — 93 curated edges connecting
  math ↔ physics (e.g. `vectors → newton_laws`, `trig_identities → ac_circuits`,
  `derivatives_intro → kinematics_1d`). Hand-curated, version 1.
- Seeder upserts these into `kg_edges` on every lesson seed.

### Mastery-aware learning-plan engine

- **`apps/web/src/lib/learning-plan.ts`** — `buildLearningPlan({ learnerId,
  goalConceptId, maxNodes })`. BFS backward walk through within-subject prereqs
  + cross-subject edges, weighted by per-atom mastery in `skill_practice`.
  Returns ordered `path[]` + `blocking_atoms[]`.
- **`GET /api/learning-plan/next?goal=<id>&max=8`** — Clerk-authenticated HTTP
  surface for the planner. Used by the agent runtime, can be used by UI.

### Six new question kinds (live)

`mcq_multi`, `true_false`, `short_answer`, `match`, `ordering`, `derivation`
joined the original `mcq`, `numeric`, `open`, `free_response`. All ten kinds:

- Render correctly in `apps/web/src/components/lesson-quiz-panel.tsx`.
- Are server-side gradeable for objective kinds via
  `apps/web/src/lib/neon-db.ts:gradeLessonAnswer` + `/api/lesson/answer/route.ts`.
- Have validation rules in `scripts/seed-lessons.mjs`.
- Have authored examples in 5 pilot lessons
  (`triangles_congruence`, `derivatives_intro`, `kinematics_1d`, `newton_laws`,
  `probability_basic`).

### HE-default language + math LTR

- **`apps/web/src/hooks/use-language-preference.ts`** — `useLanguagePreference()`
  defaults to `he`, persists in `localStorage` + `asf_lang` cookie. Used by
  `LessonPageClient` and `ConceptContentClient`.
- **`apps/web/src/app/globals.css`** — CSS overrides forcing
  `.katex, .katex-display { direction: ltr; unicode-bidi: isolate; }` so math
  always renders LTR even inside Hebrew RTL paragraphs.

### Runtime agent grounding (NEW this round)

- **`apps/web/src/lib/agent-baseline.ts`** — shared system baseline injected
  into EVERY runtime agent's system prompt. Documents the corpus stats, KG
  dimensions, agent network roster, math-LTR rule, no-external-links rule,
  bilingual rule, brand-new-learner protocol.
- **`apps/web/src/lib/agent-prompts.ts`** — long-form runtime personas for
  the 6 live chat agents (tutor, mentor, coach, reviewer, qa_explainer,
  note_taker). Versioned, with explicit tool catalogs, output format, and
  "you are part of an agent network" hand-off rules. Source of truth for the
  WEB; the `prompts/<agent>/v1.md` markdown files are kept in sync for human
  / sub-agent readers.
- **`apps/web/src/app/api/chat/route.ts`** — now composes:
  `baseline + persona + (no-profile cue if new learner) + profile + mastery
  + relevant curriculum + lesson agent_hints + learning-plan snapshot`.
- **`prompts/<agent>/v1.md`** — each updated with: math LTR rule, bilingual
  rule, agent-network hand-off section, `learning_plan.next` in the tools
  list where relevant. Placeholder `note_taker/v1.md` filled out.

### New / updated skills

- **`skills/author-lesson/SKILL.md`** — full schema for a lesson JSON,
  all 10 question kinds, `agent_hints` shape, skill-atom wiring, the seed
  command.
- **`skills/use-learning-plan/SKILL.md`** — how to consume the planner from
  agents, UI, or scripts. Per-agent recipes (Curriculum Designer, Progress
  Analyzer, Tutor, Coach, Q&A).
- **`skills/cross-subject-kg/SKILL.md`** — how to add edges to
  `kg-cross-edges.json`, the 5 relation types, naming conventions for
  skill atoms.
- **`skills/chat-memory-context/SKILL.md`** — pre-existing; should be updated
  in a follow-up to mention the baseline + persona composition (TODO below).

### Prompt updates (sub-agent readable)

- `prompts/curriculum_designer/v1.md` — documents `learning_plan.next` as
  the authoritative path planner.
- `prompts/progress_analyzer/v1.md` — documents it as the root-cause tool;
  standard recipe added.
- `prompts/tutor/v1.md`, `prompts/mentor/v1.md`, `prompts/coach/v1.md`,
  `prompts/qa_explainer/v1.md`, `prompts/reviewer/v1.md`,
  `prompts/note_taker/v1.md` — math-LTR rule, bilingual rule, agent-network
  section added.

---

## What the live agents now know on turn one

Even for a brand-new learner with zero memory, every chat agent now receives:

1. The shared baseline (corpus stats, KG dimensions, agent network, universal
   rules — math LTR, bilingual, no external links, brand-new-learner
   protocol).
2. Its own long-form persona (tools allowlist, style, hand-off rules,
   refusal/safety).
3. If profile exists: profile, mastery, relevant curriculum, lesson
   `agent_hints`, learning-plan snapshot.
4. If no profile: an explicit "brand-new learner — point them at /onboarding"
   cue.

Test this live by signing up a fresh user, going straight to `/app/chat/tutor`,
and confirming the first reply opens in Hebrew with an onboarding invite — not
an improvised curriculum.

---

## What stays exactly as-is

- All Round 7 deliverables (onboarding, diagnostic, plans, chat memory,
  external resources fallback).
- The Render backend (still optional fallback; the Vercel route remains
  Render-independent per `skills/neon-direct-route/SKILL.md`).
- All earlier migrations (0001 → 0013).
- The `external_resources` table — fallback only, not the primary content.

---

## Pending follow-ups (next rounds)

| Priority | Item                                                              | Notes                                                                                             |
| -------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| P1       | Author +6 questions per remaining ~69 lessons                     | Continuation from Round 7 brief; ID `author-bulk`. Use `scripts/seed_data/lessons/*.json` shape.  |
| P1       | Build script: `scripts/sync-agent-prompts.mjs`                    | Read `prompts/<agent>/v1.md` → write `apps/web/src/lib/agent-prompts.generated.ts`. Today it's manual. |
| P2       | Add E2E test: brand-new user → HE-default + onboarding nudge      | `apps/web/e2e/brand-new-learner.spec.ts`. Critical regression guard.                              |
| P2       | Extend `skills/chat-memory-context/SKILL.md`                      | Document baseline + persona composition; today it's stale.                                       |
| P2       | Add eval suite: cross-subject path planner                        | `evals/planning/cross-subject.yaml`. Verify `vectors → newton_laws → projectile_motion` paths.    |
| P3       | Cap & cache `buildLearningPlan` results per learner per goal      | Today it runs per chat turn that mentions a relevant concept. ~300ms warm.                        |
| P3       | Expose more agents via the website chat UI                        | Today: 6 chat agents. Curriculum Designer / Progress Analyzer / Q&A Explainer have personas but no dedicated UI tile yet. |
| P3       | Add Hebrew skill_atom names + descriptions in `skill_atoms`       | Currently EN only. The atom IDs stay EN (snake_case) — only display strings get translated.       |

---

## Quick reference — files added or changed

| File                                                          | Purpose                                                                |
| ------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `apps/web/src/lib/agent-baseline.ts`                          | Shared baseline injected into every runtime agent.                     |
| `apps/web/src/lib/agent-prompts.ts`                           | Long-form personas for live chat agents.                               |
| `apps/web/src/lib/kg-cross-edges.json`                        | 93 hand-curated cross-subject edges.                                   |
| `apps/web/src/lib/learning-plan.ts`                           | Mastery-aware path planner.                                            |
| `apps/web/src/app/api/learning-plan/next/route.ts`            | HTTP surface for the planner.                                          |
| `apps/web/src/app/api/chat/route.ts`                          | Composes baseline + persona + per-turn signals.                        |
| `apps/web/src/app/api/lesson/answer/route.ts`                 | Server-side grading for the 10 question kinds.                         |
| `apps/web/src/components/lesson-quiz-panel.tsx`               | UI for all 10 kinds.                                                   |
| `apps/web/src/components/lesson-page-client.tsx`              | HE-default via `useLanguagePreference`.                                |
| `apps/web/src/components/concept-content-client.tsx`          | HE-default via `useLanguagePreference`.                                |
| `apps/web/src/hooks/use-language-preference.ts`               | Persisted HE-default language preference.                              |
| `apps/web/src/app/globals.css`                                | `.katex { direction: ltr }` — math LTR fix.                            |
| `infra/alembic/versions/0014_kg_skill_graph.py`               | Schema for kg_edges, skill_atoms, lesson_skill_atoms, answer_payload.  |
| `scripts/seed-lessons.mjs`                                    | Validates all 10 kinds; backfills skill_atoms + lesson_skill_atoms.    |
| `scripts/audit-lessons.mjs`                                   | Corpus health report.                                                  |
| `scripts/seed_data/lessons/*.json` (5 pilot files)            | Each carries 12 questions covering all 10 kinds.                       |
| `skills/author-lesson/SKILL.md`                               | New — lesson authoring reference.                                      |
| `skills/use-learning-plan/SKILL.md`                           | New — planner consumption reference.                                   |
| `skills/cross-subject-kg/SKILL.md`                            | New — edge + skill-atom authoring reference.                           |
| `prompts/<agent>/v1.md` (tutor, mentor, coach, qa_explainer, reviewer, note_taker, curriculum_designer, progress_analyzer) | Math LTR, bilingual, agent-network sections; `learning_plan` documented. |
| `.cursor/subagent-briefs/16-phase4-knowledge-and-agent-runtime.md` | This brief.                                                       |

## Acceptance — already verified

- ✅ Math renders LTR in Hebrew lessons (CSS override in `globals.css`).
- ✅ Tutor / Mentor / Coach / etc. each receive the baseline + their long-form
  persona on every request (verified via direct read of chat route output for
  a probe user).
- ✅ Brand-new user with no profile gets the "## Brand-new learner" cue in
  their system prompt.
- ✅ `agent_hints` and `learning-plan snapshot` continue to inject when a
  learner's message mentions a covered concept.

## Rules for follow-up agents

Unchanged from Round 7:

- Conventional commits, one task = one branch = one PR.
- Lint + typecheck + unit must pass.
- Run `review-bugbot` on every PR.
- No secrets in code.
- Free-tier critical-path routes follow `skills/neon-direct-route/SKILL.md`.
- Chat persistence follows `skills/chat-memory-context/SKILL.md`.
- **NEW:** New lessons follow `skills/author-lesson/SKILL.md`.
- **NEW:** Anything that asks "what next?" / "why am I stuck?" follows
  `skills/use-learning-plan/SKILL.md` — do not hand-walk `kg.related_concepts`.
- **NEW:** New cross-subject edges or skill atoms follow
  `skills/cross-subject-kg/SKILL.md`.
- **NEW:** Anything that touches the runtime agent context (`chat/route.ts`,
  `agent-baseline.ts`, `agent-prompts.ts`) must keep the baseline + persona
  + per-turn composition order intact.
