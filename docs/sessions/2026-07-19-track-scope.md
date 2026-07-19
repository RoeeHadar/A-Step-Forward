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

## Batch H — shipped

The **entire 5pt calculus + advanced-topic core** expanded from 10-11 items to
**15 CAS-verified items each** (11 lessons, 165 items, 0 rejections):

- `limits_5pt` — substitution, indeterminate factoring, special limits
  (`sin(3x)/x`, `(1-cos x)/x²`, `tan x/x`), limits at infinity, removable
  discontinuity, one-sided non-existence.
- `derivatives_trig_exp` — power/product/chain on `sin`, `cos`, `tan`, `eˣ`,
  `x·eˣ`, `eˣ·sin x`, derivative-at-a-point.
- `derivatives_applications` — tangent lines, monotonicity, concavity, critical
  points, kinematics (v, a from s).
- `definite_integrals` — polynomial/linear/exponential/log integrals over
  `[a,b]`, mean value of a function.
- `function_analysis_5pt` — full investigation (extrema classification via
  `f''`, inflection points, increase/decrease intervals).
- `integrals_applications` — area under a curve, area between curves, volume of
  revolution (disk method, `_pl(..., "5pt")`-gated).
- `sequences_5pt` — arithmetic/geometric nth term & sums, infinite convergent
  series, term-index solving.
- `exponential_logarithmic` — log evaluation, product/quotient rules, exp
  equations (common base + `y = aˣ` substitution), domain checks.
- `complex_numbers_5pt` — modulus, conjugate, arithmetic, powers of `i`, roots
  of negatives.
- `analytic_geometry_5pt` — distance, slope, perpendicular slope, circle
  equation (standard + complete-the-square), midpoint, diameter→radius.
- `trigonometric_equations` — special-angle values, `sin/cos/tan` equation
  solving, solution counting on `[0, 2π)`, Pythagorean/supplementary identities.

All new items are pure SymPy-CAS-verifiable (numeric, MCQ-with-predicate, or
`open_worked` with a CAS check). Purged the 11 concepts' stale content-addressed
store rows before rebaking. Strict + math + depth + track-scope audits and the
207/207 seed dry-run all green; difficulty spread 4-5 kinds per lesson.

## Batch I — shipped

The **HS calculus track-variant + intro core** expanded to **15 CAS-verified
items each** (7 lessons, 105 items, 0 rejections):

- `derivatives_rules` (4pt/5pt) — topped up 11→15 (added power/quotient/chain
  drills + derivative-at-a-point).
- `limits_4pt` (4pt) — substitution, `0/0` factoring, rationalizing conjugates,
  degree-comparison at infinity, one-sided non-existence. **No special trig
  limits** (kept to 4pt scope).
- `limits` (5pt) — adds the fundamental trig limits (`sin x/x`, `sin 5x/x`,
  `(1-cos x)/x²`, `tan x/x`, `(eˣ-1)/x`) on top of the 4pt basics.
- `limits_at_infinity` (5pt) — horizontal asymptotes, degree comparison,
  `√(x²+1)-x` conjugate trick, one/both-direction limits.
- `continuity` (5pt) — function values, removable vs jump vs infinite
  discontinuities, solving for a parameter that makes a piecewise `f` continuous.
- `integrals_4pt` (4pt) — polynomial antiderivatives, definite integrals, area
  under a curve. **No by-parts / substitution / volumes** (kept to 4pt scope).
- `function_analysis_4pt` (4pt) — first/second-derivative analysis, critical
  points, monotonicity, concavity, inflection, parabola vertex/min (polynomial
  only, no rational/trig investigations).

Track discipline: the 4pt variants deliberately omit 5pt-only techniques so 4pt
learners are not shown out-of-scope material, while the 5pt siblings
(`limits`, `limits_at_infinity`, `continuity`) carry the deeper content. All
items pure SymPy-CAS-verifiable. Strict + math + depth + track-scope audits and
the 207/207 seed dry-run all green.

## Batch J — shipped

The **core algebra & functions foundation (alternate/syllabus IDs)** expanded to
**15 CAS-verified items each** (6 lessons, 90 items, 0 rejections):

- `linear_equations_basics` (3pt/4pt/5pt) — isolate, collect, distribute,
  fractional & cross-multiplied linear equations, identities.
- `linear_equations_one_variable` (3pt/4pt/5pt) — same skills with distinct
  problems + two word problems (number puzzle, rectangle perimeter) + a
  no-solution case.
- `systems_linear_equations` (3pt/4pt/5pt) — elimination, substitution,
  dependent (infinite) and inconsistent (none) systems, a word problem.
- `linear_functions` (3pt/4pt/5pt) — slope, intercepts, evaluation, line through
  two points, parallel slopes.
- `functions_intro` (3pt/4pt) — evaluation, domain exclusions, composition,
  solving `f(x)=k`.
- `functions_exponential` (4pt/5pt) — evaluate `aˣ`, `a⁰`, growth/decay word
  problems, `aˣ=b` solving, monotonicity.

All items pure SymPy-CAS-verifiable. Strict + math + track-scope audits and the
207/207 seed dry-run all green.

## Seed path fix

The `Seed DB (one-shot)` workflow under `target=all` does **not** run the lesson
question seed — that step is gated to `target=lessons-from-json` (runs
`generate-lessons-artifacts.mjs` + `seed-lessons.mjs`, a full DELETE+INSERT of all
207 lessons over Neon HTTP, ~10-13 min). Earlier `all` reseeds this session did
not push the new question banks to Neon. **Correct trigger for shipping questions:
`gh workflow run "Seed DB (one-shot)" -f target=lessons-from-json`.** (The
`target=all` Neo4j KG step also fails when the Aura free instance is paused, but
that is unrelated to learner-facing question content.)

## Batch K — shipped

The **3pt/4pt applied-foundation strand** expanded to **15 CAS-verified items
each** (6 lessons, 90 items, 0 rejections after a one-item fix):

- `fractions_and_ratios` (3pt/4pt/5pt) — add/sub/mul/div, simplify, compare,
  ratio-division, proportion, map scale, and two word problems.
- `percentages_applications` (3pt) — percent-of, discount, increase/reverse,
  VAT, simple & compound interest, markup, successive-change traps.
- `basic_statistics_3pt` (3pt) — mean/median/mode/range, weighted average,
  missing-value, combined-group averages, outlier robustness.
- `word_problems` (3pt/4pt) — distance-rate-time, mixture, work-rate, age,
  sum/difference systems, average-speed trap.
- `plane_trigonometry_right_triangle` (4pt/5pt) — Law of Sines, Law of Cosines,
  area $\tfrac12 ab\sin C$, Heron's formula, parallelogram area.
- `descriptive_stats` (3pt/4pt/5pt) — mean/median/mode/range plus population
  variance, standard deviation, quartiles and IQR (exclusive method).

**Fix during authoring:** one `descriptive_stats` variance-invariance T/F item
had a wrong shifted-mean in its verify predicate (`1+5-6` should be the shifted
value $6$ with mean $7$); corrected, purged the stale store entries, regenerated,
and re-baked to 15/15 auto-verified. Difficulty spread ≈ 33% easy / 40% medium /
27% hard, 4 kinds per lesson. Math + strict + track-scope audits and the 207/207
seed dry-run all green (Batch K adds no new strict/track violations).

## Batch L — shipped

The **coordinate-geometry / mensuration strand** expanded to **15 CAS-verified
items each** (6 lessons, 90 items, 0 rejections):

- `analytic_geometry_basic` (3pt) — distance, midpoint, slope, line equation,
  parallel/perpendicular slopes, coordinate triangle area.
- `analytic_geometry_4pt` (4pt) — circle equation (center/radius), complete-the-
  square, point–line distance, line–circle intersection, tangent length.
- `vectors_2d` (4pt/5pt) — magnitude, dot product, addition/scalar multiple,
  angle ($\cos\theta$), perpendicular/parallel tests, unit vector, projection,
  2D cross-product area.
- `3d_solids_volume` (3pt) — cube/box/prism volume & surface area, cylinder,
  cone, sphere, hemisphere, scaling law.
- `circles` (3pt/4pt/5pt) — circumference, area, arc length, sector area, ring
  area, chord length, inscribed-angle / Thales.
- `geometry_basics` (3pt) — complementary/supplementary/vertical angles,
  triangle & polygon angle sums, exterior/isosceles angles, transversal angles.

Difficulty spread ≈ 33% easy / 40% medium / 27% hard, 4 kinds per lesson. Three
functions were initially miscounted at 14 items; each got one more medium item
(box surface area, sector area, vertical angle) and re-baked to 15/15. Math +
strict + track-scope audits and the 207/207 seed dry-run all green; total strict
warnings across the corpus dropped from 1537 to 1458 as baking now exercises every
taught atom in these lessons.

## Batch M — shipped

The **algebra-review / advanced-topic strand** expanded to **15 CAS-verified
items each** (6 lessons, 90 items, 0 rejections):

- `algebra_review` (3pt/4pt/5pt) — expand/factor (incl. difference of squares,
  cubes), simplify, evaluate, rational cancellation. Uses `symbolic_equal`
  verification for the expand/factor items.
- `complex_numbers` (5pt) — real/imaginary parts, add/subtract/multiply/divide,
  modulus, conjugate, $i^2=-1$.
- `quadratic_model_fitting` (3pt) — evaluate, vertex/axis, y-intercept, fit
  $a/b/c$ from points, roots↔coefficients, vertex form.
- `linear_programming_two_variables` (3pt) — evaluate the objective at vertices,
  maximize/minimize over a vertex set, convexity/vertex-optimum theory.
- `trigonometry_equations` (4pt/5pt) — solve $\sin/\cos/\tan x=k$, double-angle,
  quadrant reasoning, cofunction identity.
- `data_representation` (3pt) — frequency totals, mode/mean/median from a table,
  relative frequency & percentage.

Difficulty spread ≈ 33% easy / 40% medium / 27% hard, 4 kinds per lesson (one
`algebra_review` item was converted from short-answer to true/false to reach 4
kinds). Math + strict + track-scope audits and the 207/207 seed dry-run all green.

## Corpus progress

Verified 15+ item banks now cover **66 math lessons** (Batches B, D, E, F, G, H,
I, J, K, L, M + exponents): the entire 3pt/4pt algebra & functions foundation
(incl. alternate syllabus IDs, algebra review, quadratic model fitting), sequences,
the core + coordinate geometry foundation (distance/midpoint/slope, circle
equations, vectors, solids/mensuration, plane-angle geometry, Law of Sines/Cosines
& Heron), the 3pt probability & statistics foundation plus descriptive statistics
(variance/SD/IQR) and data representation, fractions/ratios/percentages/word
problems, linear programming, complex numbers, trig equations, and the full 5pt
calculus + advanced-topic core plus the HS calculus track-variant + intro core.
Remaining thin lessons (8 questions): advanced 4pt/5pt conics/3D-vectors/
combinatorics/de-Moivre/induction/trig-identities, inferential statistics, and
university/makhina strands.

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
