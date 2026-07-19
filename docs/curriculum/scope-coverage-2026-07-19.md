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

### A. Coverage gap closed via a level-appropriate alias (1)

| Syllabus concept | Aliased to | Level fit |
| ---------------- | ---------- | --------- |
| `photoelectric_effect` | `modern_physics_intro` | HS → HS ✓ (that lesson already teaches the photoelectric effect) |

Only aliased where the target lesson's level matches the served track. The other
raw "gaps" fall into two categories that must NOT be alias-redirected:

- **Depth-mismatch gaps** (HS concept, only university lesson existed) — now closed
  by authoring dedicated HS lessons; see section D.
- **Intentional titled stubs** (deliberately lesson-less calc-1 theory concepts,
  guarded by `learn-routes.test.ts` — they render a titled concept page and are
  tutor-handled): `extreme_value_theorem`, `intermediate_value_theorem`,
  `sequences_monotone_bounded`, `series_absolute_convergence`,
  `convergence_divergence_integrals`.

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

### D. HS-level lessons authored to close depth-mismatch gaps (4)

Rather than mis-alias HS concepts to university lessons, four new bilingual,
level-appropriate lessons were authored (each: ≥1 theory section, 3 worked
examples, ≥15 questions across ≥3 kinds with easy/medium/hard spread, structured
`agent_hints`, every taught skill-atom exercised, 0 math-render issues). The
file name matches the catalog `concept_id`, so coverage now resolves **directly**
(no alias needed).

| New lesson | Level / track | Core content |
| ---------- | ------------- | ------------ |
| `capacitors_parallel_plate.json` | HS Physics (electricity) | $C=Q/V$, $C=\varepsilon_0 A/d$, $E=V/d$, energy $\tfrac12CV^2$, series/parallel, connected-vs-disconnected |
| `em_waves.json` | HS Physics (radiation & matter) | EM wave nature, $c=f\lambda$, the spectrum ordered by frequency, photon energy $E=hf=hc/\lambda$ |
| `normal_distribution_basics.json` | Bagrut 3pt (+4pt) | Bell shape, symmetry, mean=median=mode, empirical 68–95–99.7 rule, reading proportions |
| `normal_distribution_z_scores.json` | Bagrut 4pt (+5pt/makhina/stats) | Standardizing $z=\frac{x-\mu}{\sigma}$, standard normal table $\Phi(z)$, $P(a<X<b)$, comparing distributions, inverse (percentile→value) |

Decision on 3pt normal distribution: the new-372 statistics unit's treatment of
the normal distribution is qualitative, so `normal_distribution_basics` is
authored at a genuinely basic (empirical-rule-only, no z-table) level and kept in
the 3pt catalog rather than pruned; z-score machinery lives in the 4pt lesson.

**Result: 0 remaining depth-mismatch gaps.** All catalog concepts now resolve to
a level-appropriate authored lesson (directly or via the single
`photoelectric_effect` alias).

### Intentional titled stubs (leave as-is)

`extreme_value_theorem`, `intermediate_value_theorem`,
`sequences_monotone_bounded`, `series_absolute_convergence`,
`convergence_divergence_integrals` are deliberate lesson-less calc-1 concepts
(guarded by `learn-routes.test.ts`). They resolve to a titled concept page under
`/learn/calculus_1/concept/...` and are handled on-demand by the tutor. Author
dedicated lessons only if you want them promoted from stubs.

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

All 211 lessons (207 prior + 4 authored this pass) satisfy the structural depth
bar: ≥1 theory section, ≥2 worked examples, ≥15 questions, ≥3 question kinds,
easy/hard spread, 0 math-render issues. This pass adds the **per-level
visible-depth** guarantee on top of the corpus-wide depth guarantee.
