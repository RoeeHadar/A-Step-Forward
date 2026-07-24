---
type: active-context
updated: 2026-07-25
coordinator_status: .cursor/coordinator/STATUS.md
production_web: "78e786da"
---

# Active Context

> Update this note at the start/end of each focused work session.
> Machine-readable session trail: `docs/reviews/LAST_DONE.md` + `MEMORY_SNAPSHOT.md` (`<!-- LAST_SESSION -->`).

## Last done (2026-07-25)

- [x] **Next-cycle backlog closed** — cross-instance memory claims + FIFO crons; chat plan-context dedupe; week-2 mirror removed; **21 Bagrut gap lessons** authored + schema/facet/KaTeX CI green. Tip `78e786da`.
- [x] **Lesson corpus** — 327 lesson JSON files; **45 KG concepts still without lessons** (≈33 `uni_*`, rest physics-track).
- Details: `docs/reviews/LAST_DONE.md` § 2026-07-25.

## Last done (2026-07-19)

- [x] **ADR-0009 living plan shipped** — anchored frontier selection (no "start at arithmetic"),
  weekly re-pace from mastery + trailing velocity, gate-pass → advance. Prod `d67a7ac0`.
- [x] **Grilling #2 → [ADR-0010](../docs/adr/0010-assessment-driven-progression.md)** —
  assessment-driven progression: advancement is EARNED via gates/tests, not lesson completion.
  16 decisions; phased streams A–F.
- [x] **ADR-0010 Stream A SHIPPED — earned advancement / breeze-through loophole closed.**
  `lesson-complete.ts`: mastery bump 0.7 → 0.35 exposure (below floors), `maybeCompleteActiveWeek()`
  removed → lessons never advance the plan. `evaluateGatePass()` (aggregate ≥ 0.75 AND every
  frontier-CRITICAL concept ≥ 0.6). `advanceRollingPlanWindow` hard gate (only gate-completed
  advances) + soft override (>14d overdue OR ≥3 retakes) + remediation carry-forward.
- [x] **ADR-0010 Streams B–F cores SHIPPED** (`942dd4d0` E+decay, `c6c89fed` B, + D/F this ship):
  - **E (readiness):** `readiness.ts` — decay-applied critical coverage → concave (80→85 harder than
    50→55), mock-gated (≤0.70 w/o mock), capped <1.0 (never "guaranteed"); phases day_before/final/building;
    surfaced on plan banner (HE/EN humble copy).
  - **C (decay):** FSRS `decayMastery` (45d half-life) feeds readiness.
  - **B (anti-gaming):** gate retake rotation (fresh items) + mock exams archived into `test_attempts`
    (feeds mock-gate) + kind-aware Tests archive.
  - **D (#15):** active wellbeing bias lightens `weekly_load` (never the pass bar).
  - **F:** `assessment-calibration.test.ts` ground-truth guardrails.
- **Deferred (in ADR):** milestone generator + open-response grading, prereq probes/anchor-lowering,
  at-risk Mentor routing, returning-learner warm-up, elevation prompts, mechanical final-phase mode,
  full promptfoo/DeepEval harness (no live learners yet).
- [x] **Manual-test ground prepped** — `scripts/seed-pilot-demo.mjs` (6 variants: `fresh`,
  `building`, `at-risk`, `near-exam`, `day-before`, `goal-complete`) + `docs/qa/adr-0010-manual-test-plan.md`
  (decision → variant → steps → expected, 16 cases). Pilot account currently seeded **`building`**
  (~70% mock-gated, 3 plan weeks — richest interactive start).
- [x] **Bagrut-depth exam corpus SHIPPED** (`1eac2606`) — ~278 original multi-part items;
  weekly gates / custom quizzes / HS mocks prefer corpus; hard-only custom quizzes; open-only
  Bagrut mocks (no MCQ quota). Rebuild: `pnpm exam-style:build`.

## Last done (2026-07-12)

- [x] **Onboarding plan WORKS** — thin `onboarding-plan-bootstrap.ts` (no neon-db on submit); 2 weeks × ≤4 concepts; `/api/plans/bootstrap` fallback
- [x] **Diagnostic gate removed** — goals/features → create plan; calibrate while learning
- [x] **Trial-and-error logged** — `.cursor/skills/diagnostic-plan-golden-path/SKILL.md` + `obsidian-vault/coordination/streams/diagnostic-plan-fixes.md`
- [x] Root cause of `FUNCTION_INVOCATION_TIMEOUT`: importing neon-db/kg-data + advisory-lock transactions on critical path — **do not reintroduce**

## Current focus

- **Stream**: Pilot — verify rolling `advanceRollingPlanWindow` over real week boundaries; smoke onboarding → `/app` plan
- **Status**: First-plan create **shipped** on `main` (`1d44e8cc`)
- **Policy**: Obsidian vault documents architecture; repo code implements it
- **Must-read before touching plan/onboarding**: `.cursor/skills/diagnostic-plan-golden-path/SKILL.md`
- [x] **MCP vault connection verified (2026-07-24)** — global `asf-obsidian` + project `obsidian` both live via `scripts/mcp-obsidian-vault.mjs` → MCPVault over `obsidian-vault/` (183 notes). Space-safe `node`+argv launcher (no `cmd /c`).

## Prior (2026-07-11)

- [x] **Unified planner (ADR-0007 / PR1)** — `generateLearningPlan()` delegates to `buildUnifiedPlanConceptOrder()` → `buildLearningPlan()` via `plan-worklist.ts`
- [x] **Wellbeing module (ADR-0008 / PR2–PR3)** — `wellbeing-plan-bias.ts`, morale blending, cooldown gates
- [x] **Chat context compaction (PR3)** — compact baseline, 4-turn session-gated memory
- [x] **ADR-0008 accepted** — doc reconciliation
- [x] **Wellbeing hooks** — `adaptive-plan-refresh.ts` (must not clobber fresh onboarding plans)

## Shipped (2026-07-03)

### Frontend (`e645aa1`)

- [x] Memory tab — read-only snapshot (profile, persona, plan focus, scoped mastery, agent notes)
- [x] Template-only plan apply — sidebar **עדכון תוכנית לימוד** alone
- [x] `concept-scope.ts` — plan-scoped weak/strong; lesson-index subject resolution
- [x] Tutor redirect on casual plan-change requests (baseline + turn injection)
- [x] Weekly quiz locale + plan-week concepts

### Curriculum / KG (earlier 2026-07-03)

- [x] KG enrichment — **156/156** concepts, all ≥5 skill atoms, all `level_scope` filled
- [x] Vault — **156** notes, all `data_completeness: full`
- [x] Lessons — **207/207** marked done in expansion queue
- [x] MCP **`asf-obsidian`** connected

## Vault updates (this session)

- [x] [[curriculum/learning-path-architecture|Learning path & GraphRAG architecture]] — unified planner + wellbeing module
- [x] ADR index — 0007 via 0008, 0008 accepted
- [x] Skills — `chat-memory-context`, `use-learning-plan`

## Next (priority order)

1. **Author remaining 45 lesson gaps** — `uni_*` + physics, ordered by plan demand (see `docs/reviews/LAST_DONE.md` § Next cycle)
2. **Seed prod Neon** for the 21 new Bagrut lessons if drift check fails; keep files as SoT
3. **Pilot smoke** — onboarding → Active week agents → week training card → gate on a real account
4. **Deepen facet questions** on the new Bagrut lessons (replace tag-only coverage where Bagrut method marks matter)
5. **Neon migrations backlog** — 0015 `plan_schema_version`, 0016 wellbeing columns, 0017 merge heads (if still open)

## KG pipeline

```
content/knowledge-graph/*.yaml
        ↓  pnpm vault:build-kg
apps/web/src/lib/kg-data.json
        +
apps/web/src/lib/kg-cross-edges.json  →  learning-plan.ts (backward walk)
        ↓  pnpm vault:sync-concepts
obsidian-vault/concepts/*.md
```

## Links

- [[Home|Vault home]]
- [[curriculum/learning-path-architecture|Learning paths]]
- [[product/plan-and-memory|Plan & memory]]
- [[curriculum/kg-workflow|KG → vault workflow]]
- [[curriculum/expansion-dashboard|Expansion dashboard]]
- [[coordination/streams/01-frontend|Frontend stream]]
