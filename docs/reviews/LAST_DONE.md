# Last done

> Short, retrievable log of completed Coordinator / reviewer work.
> Agents and humans: read this (and `MEMORY_SNAPSHOT.md` `<!-- LAST_SESSION -->`) before re-deriving status.

## 2026-07-25 — Next-cycle backlog shipped (memory claims, UX polish, 21 lessons)

**Goal:** Close the five deferred items from the 2026-07-24 product-completeness release, then leave `main` green.

| Checkpoint | Done? | Evidence |
|------------|:-----:|----------|
| Cross-instance dream/consolidation DB claims | [x] | `last_dreamed_at` / `consolidation_started_at` via `ensureMemoryClaimColumns` + `UPDATE…RETURNING` |
| Cron FIFO by oldest live notes | [x] | `GROUP BY learner_id ORDER BY MIN(created_at)` |
| Chat plan-context dedupe (Active week + one-liner) | [x] | `buildPlanHeaderLine` + route wiring |
| Remove deceptive week-2 concept mirror | [x] | bootstrap + dashboard "unlocks after Week 1" nudge |
| Author 21 priority Bagrut math gap lessons | [x] | `scripts/seed_data/lessons/*` — pass `validateLessonStrict` + facet audit |
| Facet checklist + KaTeX Hebrew CI recovery | [x] | tip `78e786da`; Lint & Test success |

**Tip:** `78e786da` — production smoke `/`, `/sign-in`, `/learn` → 200.

### Next cycle (priority)

1. **Curriculum — remaining 45 KG concepts without lessons** — almost all `uni_*` + physics-track. Prioritize by live plan demand / onboarding subject mix, not alphabetical. Keep facet pilot families green when adding.
2. **Seed Neon from the 21 new JSON lessons** — if production Neon counts lag files, run seed + `scripts/verify-seed-drift.mjs` (files remain SoT).
3. **Facet pedagogy depth** — several new lessons satisfy the facet gate via tags; upgrade tagged stubs into genuine graphical / rule-selection / table / identity items where method marks matter for Bagrut.
4. **Pilot golden-path smoke on a real account** — onboarding → plan → Active-week chat anchoring → week training card → gate. Document any residual UX gaps.
5. **Optional:** merge residual Tutor/Mentor plan-header redundancy further only if prompt budgets regress under load.

## 2026-07-07 — Code-review fixes + CI noise

**Goal:** Land remaining review findings and stop scheduled red X’s on `main`.

| Checkpoint | Done? | Evidence |
|------------|:-----:|----------|
| Architecture Steward groundwork (skill + brief 24) | [x] | `.cursor/skills/architecture-review/`, `.cursor/subagent-briefs/24-architecture-steward.md` |
| Code Reviewer groundwork (skill + brief 25) | [x] | `.cursor/skills/code-review/`, `.cursor/subagent-briefs/25-code-reviewer.md` |
| Platform architecture assessment | [x] | `docs/architecture/assessments/2026-07-05-platform-overview.md` |
| Coordinator-fixes code review (R1–R7 written) | [x] | `docs/reviews/2026-07-05-coordinator-fixes.md` |
| R1 — xact advisory lock (Neon HTTP-safe) | [x] | `neon-db.ts` `pg_try_advisory_xact_lock` inside `sql.transaction` |
| R2 — plan DELETE+INSERT transactional | [x] | `generateLearningPlan` persist batch in one `transaction` |
| R3 — `dbConfigured === false` → 503 | [x] | `/api/dashboard`, `/api/memory` |
| R4 — DB errors logged + 503 via `NeonQueryFailedError` | [x] | same routes + snapshot helpers |
| R5 — unit tests (mapper / lock helpers) | [x] | `apps/web/src/lib/neon-db-mapper.test.ts` |
| Keep Render warm never fails the schedule | [x] | `ff021ca9` best-effort `exit 0`, 90s timeout |
| Cron/warm jobs declare `permissions: contents: read` | [x] | keep-warm, cron-dreaming, cron-decay, cron-consolidate |

**Commits**

- `362f813b` — neon-direct routes, transactional locks, agent review groundwork
- `ff021ca9` — keep-warm exit policy + read-only permissions on cron/warm workflows

**Not in scope / not started**

- Dual planner unification (ADR-0007 follow-up)
- Adding `permissions:` to *every* deploy/lint workflow
- Anything named ProServAI / Gong / scorg — **not this repository**

## How to load next session

1. Open `docs/reviews/LAST_DONE.md` (this file).
2. Open `MEMORY_SNAPSHOT.md` block between `<!-- LAST_SESSION -->` markers (also loaded by `agentStart` hooks).
3. Open `obsidian-vault/_active-context.md` for product next steps.
