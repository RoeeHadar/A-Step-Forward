# 2026-07-19 — Track-scoped math corpus fan-out (autonomous session)

Continuation of the math-corpus rewrite. This session's mandate (from the
grill-me decisions log): make every HS Bagrut math lesson **track-appropriate**
so no learner is shown material outside their track's MoE scope, with deeper &
broader verified questions.

## Decisions in force (from grill-me)

- **Representation:** per-track **variant lessons** (track-suffixed ids like
  `limits_4pt`/`limits_5pt`) only where a multi-track concept's MoE scope/depth
  genuinely differs; foundational/identical concepts stay a single shared lesson.
- **Scope authority:** MoE Bagrut questionnaires (372/472/572 + old 382/482/582)
  cross-checked with `apps/web/src/lib/curriculum-categories.ts`. **kg-data.json
  `points_levels` is advisory only** (it disagrees with MoE in several places).
- **Membership prunes:** applied by best judgment while user offline; logged here.
- **Depth:** full theory + 15+ verified questions, ~30/40/30 easy/med/hard,
  4-5 kinds, track-calibrated (deferred items below — volume expansion pending).
- **Verification:** CAS/deterministic only shipped as graded; non-verifiable →
  `needs_review`, not baked.
- **Gates:** CAS, strict, math-lint, depth, unit tests + new `audit-track-scope`.
- **Shipping:** commit + push + reseed prod per batch, full deploy verification.

## Root-cause bug fixed (corpus-wide, high severity)

The SymPy generator defaulted every item's `points_level` to **`5pt`**. Baked
into lessons, this set `points_level_min: "5pt"` on **every** question — so on a
3pt/4pt concept like `functions_quadratic` (tracks `["3pt","4pt"]`) the quiz
panel hid **all** questions from the only learners it serves. Every batch-1 and
Bagrut-5 pilot lesson was affected.

**Fix:** `scripts/gen/generate_math_items.py` now derives the default
`points_level` from the lesson's **lowest** `math_track`, and exposes `_pl(item,
level)` to raise individual advanced items. `scripts/bake-question-items.mjs`
prefers per-item `points_level_min`.

## Batch A — shipped

Track-gating correctness across the 18 generator-backed concepts + `math_track`
repairs. All gates green (unit 8/8, math-lint 0, strict 0, track-scope 0 errors).

### `math_track` corrected
- `logarithms` `[]` → `["4pt","5pt"]`
- `derivatives_rules` `["calc1"]` → `["4pt","5pt"]`
- `integrals_applications` `["calc1","5pt"]` → `["4pt","5pt"]`
- `derivatives_trig_exp` `["5pt","university"]` → `["5pt"]`
- 16 lessons had **empty** `math_track` (couldn't gate at all) — assigned:
  foundational (algebra_review, fractions_and_ratios, geometry_area_perimeter,
  linear_equations_basics, linear_equations_one_variable, linear_functions,
  circle_area_circumference, quadrilaterals, sample_space,
  systems_linear_equations) → `["3pt","4pt","5pt"]`;
  `euclidean_geometry_circles` → `["4pt","5pt"]`; `mathematical_induction` →
  `["5pt"]`; `percentages_and_interest`, `percentages_applications` → `["3pt"]`;
  `word_problems` → `["3pt","4pt"]`; `quadratic_equations_makhina` → `["makhina"]`.

### 18 concepts re-baked (correct gating, 0 CAS rejections)
algebra_basics, factoring, equations_quadratic, functions_quadratic, logarithms,
exponents, derivatives_rules, derivatives_trig_exp, derivatives_applications,
function_analysis_5pt, integrals_applications, sequences_5pt,
exponential_logarithmic, complex_numbers_5pt, analytic_geometry_5pt,
trigonometric_equations, limits_5pt, definite_integrals.

### New tooling
- `scripts/audit-track-scope.mjs` (+ `pnpm audit:lessons:track-scope`): flags
  questions gated above every served track (the bug above), empty `math_track`,
  per-track visible-question counts, and kg-data cross-check.

## Advisory follow-ups (kg-data vs math_track — verify against MoE)

`audit-track-scope` reports 27 advisory mismatches vs kg-data. Because kg-data is
NOT the authority these are expected; spot-verify a few (e.g. `sequences_geometric`
kg=`["4pt","5pt"]` vs `["3pt","4pt"]`; `triangles_congruence`).

## Batch B — shipped

Volume + diversity for the six highest-traffic 3pt/4pt foundational lessons
(`algebra_basics`, `factoring`, `equations_quadratic`, `functions_quadratic`,
`logarithms`, `exponents`): each expanded from 10 → **15-16 CAS-verified items**,
spanning 5 kinds with an easy/med/hard spread and multi-step bilingual solutions.
New items target distinct sub-skills (sign traps, factor theorem, factor-by-
grouping, Vieta, completing the square, change of base, negative/fractional
exponents, consecutive-integer word problem). 0 CAS rejections; all gates green.

## Batch C — shipped

Per-item `points_level_min` was being dropped by `normalizeForStore`
(`scripts/lib/question-store-io.mjs`), so `_pl(..., "5pt")` tags never reached
the baked lesson. Fixed the normalizer, then gated the `volume_of_revolution`
MCQ in `integrals_applications` to 5pt so 4pt learners (who reach it via the
`areas_between_curves` alias) no longer see 5pt-only solid-of-revolution work.
Regenerated + rebaked: 10 items stay 4pt, 1 raised to 5pt. All gates green.

## Batch D — shipped

Two new **verified generators** for high-traffic 3pt/4pt concepts that had no
generator and only ~8 hand-authored questions:

- `sequences_arithmetic` → **15 CAS-verified items** (nth term, common
  difference, finite sums, Gauss pairing, symmetry, term-index solve, two-
  equation system, sum-target word problem). All 3pt-visible.
- `sequences_geometric` → **15 CAS-verified items** (nth term, ratio, finite
  sum, doubling growth word problem, infinite series). The **4 infinite-series
  items** (S∞ convergence, `|q|<1` reasoning, bouncing-ball) are gated to `4pt`
  with `_pl(..., "4pt")` — 3pt learners see the 11 finite-sequence items only,
  keeping the lesson track-appropriate.

0 CAS rejections across all 30 items; strict + math + track-scope audits and the
seed dry-run (207/207) all green.

## Batch E — shipped

Six new **verified generators** for the highest-traffic 3pt/4pt algebra &
functions core (each previously ~8 hand-authored questions, no generator), now
**15 CAS-verified items each** (90 total, 0 rejections):

- `equations_linear` (3pt/4pt) — linear solves, literal equations, 2×2 systems,
  bilingual word problems.
- `functions_linear` (3pt/4pt) — evaluate, slope, intercepts, slope-from-two-
  points, parallel/perpendicular, line equations, intersection.
- `inequalities` (3pt/4pt/5pt) — linear + compound inequalities at 3pt; the **5
  quadratic-inequality / sign-analysis items gated to 4pt** so 3pt learners stay
  in scope.
- `arithmetic` (3pt) — fraction ops, order of operations, integer powers,
  complex fractions, recipe word problem.
- `fractions_algebraic` (3pt/4pt) — simplify/combine rational expressions,
  domain restrictions, complex-fraction reveal.
- `percentages_and_interest` (3pt) — percent-of, increase/decrease, reverse
  percentage, simple + compound interest, successive-discount trap.

Each has a calibrated easy/med/hard spread across 4–5 kinds with multi-step
bilingual solutions. Strict + math + track-scope audits and the 207/207 seed
dry-run all green.

## Batch F — shipped

Four new **verified generators** for the highest-traffic geometry/trig foundation
lessons (3pt/4pt/5pt, previously ~8 hand-authored, no generator), now **15
CAS-verified items each** (60 total, 0 rejections):

- `pythagorean_theorem` — hypotenuse/leg, triples, converse, distance formula,
  ladder + square-diagonal word problems.
- `trigonometry_ratios` — SOH-CAH-TOA, special angles (30/45/60), solving for a
  side, hypotenuse+sine reveal.
- `geometry_area_perimeter` — rectangle/triangle/parallelogram/trapezoid area &
  perimeter, composite shapes, inner-path word problem.
- `circle_area_circumference` — area, circumference, arc length, sector area,
  semicircle, reverse (radius from circumference), fence word problem.

**Math-lint catch:** the first bake put Hebrew inside `\text{}` within math spans
(e.g. `\dfrac{\text{מול}}{\text{יתר}}`), which KaTeX cannot render. Fixed by
moving Hebrew descriptors outside the math. Note: the file-backed question store
is content-addressed, so regenerating after an edit leaves stale copies — purge
the concept's store rows before rebaking (done here). Strict + math + track-scope
audits and the 207/207 seed dry-run all green.

## Batch G — shipped

Four new **verified generators** for the 3pt probability & statistics foundation
(previously ~8 hand-authored, no generator), now **15 CAS-verified items each**
(60 total, 0 rejections):

- `statistics_descriptive` — mean, median, mode, range, weighted average,
  missing-value-from-mean reveal.
- `probability_basics_3pt` — favorable/total, complement, deck/bag/spinner,
  probability range.
- `sample_space` — counting outcomes, multiplication principle, dice/coins,
  menu-combinations reveal.
- `probability_conditional_3pt` — independent multiplication, without-replacement
  dependent draws, conditional formula.

**Two more file-store gotchas caught & fixed:**
1. *Duplicate stem collision* — `sample_space` had a `num` and an `mcq` sharing an
   identical stem; the content-addressed store ID (concept+source+stems) deduped
   them to 14. Reworded the mcq stem → 15.
2. *Hebrew in `\text{}`* — `$P(\text{שניהם אדומים})$`-style notation is Hebrew
   inside a math span (KaTeX can't render). Moved every Hebrew event description
   out of the math into prose. **Takeaway:** in probability, keep `$P(\dots)$`
   arguments ASCII (`A'`, `A\cap B`) or describe the event in Hebrew prose.

All audits + seed dry-run (207/207) green.

## Corpus progress

Verified 15+ item banks now cover **24 math lessons** (Batches B, D, E, F, G +
exponents): the entire 3pt/4pt algebra & functions foundation, sequences, the core
geometry/trig foundation, and the 3pt probability & statistics foundation.
Remaining thin lessons (8 questions): the 5pt calculus core (11 each), advanced
4pt/5pt geometry/trig/probability, and university/makhina strands.

## Pending (not yet done this window)

- **Volume:** expand remaining generators to 15+ items each (5pt calculus core
  still 10-11).
- **Within-lesson 5pt tags:** in mixed 4pt/5pt lessons (integrals_applications
  volumes/shells, derivatives_applications related-rates) raise 5pt-only items
  with `_pl(..., "5pt")` so 4pt learners don't see 5pt-only work.
- **Full theory rewrites** (Q14) for the corpus.
- **Variants** where MoE depth genuinely differs (rarer than first estimated —
  most shared concepts only need per-item tagging, handled by the base fix).
- **Membership prunes** of out-of-scope concepts from track categories.
- **Non-symbolic strands** (geometry proofs, word problems, probability):
  author + `needs_review`, defer from graded.
