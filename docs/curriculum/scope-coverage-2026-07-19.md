# Track Scope & Coverage Audit — 2026-07-19

Quality pass verifying that **every lesson aligns with the material needed for its
level**, and that **all required material is covered, in depth**, across the 12
curriculum tracks. Authority: official MoE Bagrut syllabus (new 172/371/372,
471/472, 571/572 + old-track questionnaires) cross-checked with
`apps/web/src/lib/curriculum-categories.ts`.

## Three sources of truth

| Source | Role |
| ------ | ---- |
| `curriculum-categories.ts` (`concept_ids` per category + `sections`) | **Authoritative** — drives what each level browses on `/learn` |
| `concept-aliases.ts` | Maps syllabus concept slugs → authored lesson ids (closes gaps without duplicate authoring) |
| lesson JSON `math_track` + question `points_level_min` | Gates diagnostic/quiz question selection + per-question visibility |

## What was checked (automated)

1. **Gating mechanics** — `scripts/audit-track-scope.mjs` → **0 errors** (29 advisory
   `math_track` vs `kg-data` cross-check warnings; see "Known advisory deltas").
2. **Coverage completeness** — every catalog concept per level resolves (directly or
   via alias) to an authored lesson.
3. **Visible depth per served level** — new `scripts/audit-track-visible-depth.mjs`:
   for every level the *catalog* serves a concept to, the lesson must expose ≥15
   questions visible to that level. Catches lessons whose questions are all gated
   above a track the catalog still serves. Old-track-only (382) calculus excluded.
4. **Math rendering** — `scripts/audit-lesson-math.mjs` → 0 issues.

## Fixes applied this pass

### A. Coverage gaps closed via level-appropriate aliases (9)

| Syllabus concept | Aliased to | Level fit |
| ---------------- | ---------- | --------- |
| `photoelectric_effect` | `modern_physics_intro` | HS → HS ✓ |
| `normal_distribution_z_scores` | `statistics_inference` | 4pt/makhina/stats (dedupes uni) |
| `extreme_value_theorem` | `absolute_extrema` | calc1 → uni ✓ |
| `intermediate_value_theorem` | `continuity` | calc1 → uni ✓ |
| `sequences_monotone_bounded` | `series_convergence_tests` | calc1 → uni ✓ |
| `series_absolute_convergence` | `series_convergence_advanced` | calc1 → uni ✓ |
| `convergence_divergence_integrals` | `improper_integrals` | calc1 → uni ✓ |

Coverage before: 12 gaps across 4 levels. After: **3 honest gaps** (below).

### B. Lessons where a required level saw ZERO questions (3)

The catalog served these to a track, but every question was gated above it —
so those learners landed on the lesson and saw nothing. All questions were
inspected and confirmed level-appropriate for the under-served track, then
un-gated and `math_track` corrected.

| Lesson | Before | After | Why |
| ------ | ------ | ----- | --- |
| `functions_exponential` | `math_track [4pt,5pt]`, 15/15 gated to 4pt | `[3pt,4pt,5pt]`, ungated | Exponential functions are a new-372 3pt topic |
| `function_transformations` | `[5pt]`, 15/15 gated to 5pt | `[3pt,4pt,5pt]`, ungated | Basic shifts/reflections of x² — 3pt topic |
| `linear_programming` | `[4pt]`, 15/15 gated to 4pt | `[3pt]`, ungated | Linear programming is the flagship new-372 (372) 3pt topic |

### C. New permanent guard

`scripts/audit-track-visible-depth.mjs` added so this bug class (catalog serves a
level the lesson gates out) is caught in future authoring. Currently **OK (0
under-served)**.

## Remaining honest gaps (need level-appropriate authoring — NOT mis-aliased)

These three were intentionally left un-aliased: the only candidate lessons are
**university-level**, and redirecting HS learners there would violate "in depth
appropriate for level" (guarded by `lesson-concept-resolve.test.ts`).

| Concept | Level(s) needing it | Only existing lesson | Recommendation |
| ------- | ------------------- | -------------------- | -------------- |
| `capacitors_parallel_plate` | HS Physics (electricity) | `capacitors_dielectrics` (university) | Author HS-level capacitors lesson |
| `em_waves` | HS Physics (radiation & matter) | `em_waves_propagation` (university) | Author HS-level EM-waves lesson |
| `normal_distribution_basics` | Bagrut 3pt | `statistics_inference` (university) | Verify 372 truly requires normal distribution; if so author HS-basic lesson, else prune from 3pt catalog |

## Deliberate design confirmed (not bugs)

- **Calculus in 3pt** (`limits_4pt`, `derivatives_intro/rules`, `integrals_intro`)
  is exposed only through the `calculus_old_track_3pt` section, flagged
  `old_track_only: true` and rendered with a clear "Old Track Only (382)" label.
  New-372 learners correctly see 0 questions there. Consider hiding this section
  entirely once the 382 cohort is fully sunset.

## Known advisory deltas (documented, not shipped)

29 `audit-track-scope` warnings remain — all the advisory "lesson `math_track`
differs from `kg-data.json` `points_levels`" cross-check. These do **not** affect
learner scope (the catalog + aliases drive browse; `math_track` drives
diagnostic/quiz selection). Reconciling `kg-data.points_levels` to the catalog is
a separate low-risk consistency pass; deferred to avoid perturbing the KG planner
without a dedicated verification.

## Depth status

All 207 lessons already satisfy the structural depth bar from prior passes: ≥1
theory section, ≥2 worked examples, ≥15 questions, ≥3 question kinds, easy/hard
spread, 0 math-render issues. This pass adds the **per-level visible-depth**
guarantee on top of the corpus-wide depth guarantee.
