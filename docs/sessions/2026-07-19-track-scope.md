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

## Batch N — shipped

The **combinatorics / geometry / modelling strand** expanded to **15 CAS-verified
items each** (6 lessons, 90 items, 0 rejections after one fix):

- `combinatorics` (4pt/5pt) — factorial, permutations $P(n,k)$, combinations
  $\binom{n}{k}$, symmetry, committee/handshake/independent-choice counts.
- `exponential_growth_decay_models` (4pt) — doubling/halving, half-life,
  compound growth $P(1+r)^t$, depreciation.
- `function_transformations` (5pt) — vertical/horizontal shifts, stretch/
  compression, reflection, combined transforms evaluated at points.
- `similar_triangles` (3pt/4pt/5pt) — scale factor, proportional sides,
  area ratio $=k^2$, perimeter ratio $=k$, shadow problems.
- `quadrilaterals` (3pt/4pt/5pt) — rectangle/square/parallelogram/trapezoid/
  rhombus/kite area & perimeter, angle sums, diagonals.
- `linear_programming` (4pt) — objective evaluation, corner-point intersection,
  vertex maximization/minimization, non-unique optimum theory.

**Fix during authoring:** the growth open-worked item had a hand-typed claimed
value (`7401.221542`) that disagreed with $5000\cdot 1.04^{10}\approx 7401.221425$
beyond the $10^{-6}$ CAS tolerance; corrected and re-baked to 15/15. `similar_
triangles` was also initially miscounted at 14 and got one more medium item.
Difficulty spread ≈ 33/40/27, 4 kinds per lesson. Math + strict + track-scope
audits and the 207/207 seed dry-run all green.

## Batch O — shipped

The **integral-calculus + vectors + analytic-geometry + trig-identities strand**
expanded to **15 CAS-verified items each** (6 lessons, 90 items, 0 rejections):

- `integrals_intro` (calc1/5pt) — definite integrals via the power rule, FTC,
  linearity, odd-symmetry shortcut. A new `defint` module helper runs each item
  through the CAS `integral_definite` check (real ground-truth, not a tautology).
- `integrals_techniques` (calc1/5pt) — u-substitution, linearity, $\int 1/x$,
  reverse-chain patterns, odd-symmetry.
- `vectors_plane` (4pt) — magnitude, dot product, components, scalar multiple,
  angle/perpendicularity, unit vector, projection, 2D cross-area.
- `vectors_dot_product_3d` (5pt) — 3D magnitude, dot product, angle, parallel/
  perpendicular tests, unit vector, projection.
- `analytic_geometry` (4pt/5pt) — slope, midpoint, distance, intercepts, line
  equations, parallel/perpendicular slopes, circle center & radius.
- `trigonometry_identities` (4pt/5pt) — special angles, Pythagorean identity,
  double-angle & sum identities, quotient identity — all verified numerically at
  concrete angles via the CAS `truth`/`value` checks (KaTeX-safe, no HE in math).

Difficulty spread 5/6/4 (≈33/40/27), 4 kinds per lesson. Math + strict +
track-scope audits all green. Zero rejections on the first pipeline pass.

## Batch P — shipped

The **applied-statistics + advanced-conics + integral-calculus strand** expanded
to **15 CAS-verified items each** (6 lessons, 90 items, 0 rejections):

- `quadratic_equations_makhina` (Makhina) — discriminant, Vieta sum/product,
  vertex & minimum, quadratic formula, root verification via CAS `expr_value`.
- `linear_regression_3pt` (3pt) — means, least-squares slope $b=S_{xy}/S_{xx}$,
  intercept $a=\bar y-b\bar x$, prediction, residual — all real datasets computed
  and CAS-verified.
- `binomial_distribution_bernoulli` (statistics) — $\binom{n}{k}$, PMF
  $\binom{n}{k}p^k q^{n-k}$, mean $np$, variance $np(1-p)$, complement.
- `analytic_geometry_conics` (5pt) — ellipse $a,b,c$, eccentricity $c/a$,
  parabola $y^2=4px$ focus & vertex form.
- `integrals_trig_exp` (5pt) — definite integrals of $\sin,\cos,e^x,e^{2x}$,
  odd-symmetry, a by-parts $\int xe^x$ — every item run through CAS
  `integral_definite`.
- `scatter_plot_correlation_intro` (statistics) — means, covariation sign,
  Pearson $r=S_{xy}/\sqrt{S_{xx}S_{yy}}$, "correlation ≠ causation".

`linear_regression_3pt` was initially 14 (a dropped medium item) and got one
more mean item. Spread 5/6/4, 4 kinds per lesson. Math + strict + track-scope
audits green; zero rejections on the first pipeline pass for all six.

## Batch Q — shipped

The **multivariable-calculus + linear-algebra + advanced-integration strand**
expanded to **15 CAS-verified items each** (6 lessons, 90 items, 0 rejections):

- `partial_derivatives` (calc2/multivariable) — $f_x$, $f_y$ via the CAS
  `derivative` check *with the correct variable*, evaluation at points, chain
  rule $\partial_x\sin(xy)$, gradient magnitude, Clairaut. First strand to hit
  **5 question kinds** (short-answer symbolic derivatives added).
- `determinants_cramer` (linear algebra) — 2×2 & 3×3 determinants (cofactor
  expansion), singular test, Cramer's rule for 2×2 systems.
- `improper_integrals` (calc1/5pt) — $\int_1^\infty x^{-p}$, $\int_0^\infty
  e^{-x}$, $\int_0^\infty (x^2+1)^{-1}=\pi/2$, $\int_0^\infty xe^{-x}=1$ — CAS
  `integral_definite` with `oo` bounds, plus the $p$-test.
- `integration_partial_fractions` (calc1/5pt) — log integrals and true partial-
  fraction decompositions $\tfrac{1}{x(x+1)}=\tfrac1x-\tfrac1{x+1}$, all CAS
  `integral_definite`-verified.
- `riemann_integral_ftc` (5pt/university) — FTC parts 1 & 2, area-as-integral,
  polynomial definite integrals.
- `combinatorics_5pt` (5pt) — $\binom{n}{k}$, permutations, inclusion-exclusion
  for 2 & 3 sets, divisibility counting, Pascal's identity.

Spread 5/6/4, 4–5 kinds per lesson. Math + strict + track-scope audits green;
zero rejections on the first pipeline pass for all six.

## Batch R — shipped

The **calculus-applications + multivariable + complex/linear-algebra strand**
expanded to **15 CAS-verified items each** (6 lessons, 90 items, 0 rejections
after one dedup fix):

- `derivatives_implicit` (calc1) — $dy/dx=-F_x/F_y$ on circles, parabolas,
  hyperbolas, ellipses; tangent vs normal slope; horizontal-tangent case.
- `optimization_related_rates` (calc1) — square/cube area & volume rates, the
  ladder $x^2+y^2=c$ relation, product-rule area rate, max-rate-is-zero.
- `double_integrals` (calc2) — iterated integrals over rectangles, separable
  factoring, constant/linear/quadratic integrands.
- `gradient_directional_derivative` (calc2) — $\nabla f$ components, magnitude,
  directional derivative $\nabla f\cdot u$, max-rate = $|\nabla f|$.
- `complex_numbers_de_moivre` (5pt) — modulus, $|z^n|=|z|^n$, De Moivre powers,
  $|\cos\theta+i\sin\theta|=1$, real/imag parts of $(1+i)^2$.
- `matrix_operations_inverse` (linear algebra) — 2×2 inverse entries via the
  adjugate formula, determinant prerequisite, $(AB)^{-1}=B^{-1}A^{-1}$.

**Fix during authoring:** the `matrix_operations_inverse` open-worked item
duplicated a medium item's stem (same matrix/entry), so the content-addressed
store deduped it to 14; changed it to a distinct matrix and re-baked to 15/15.
Spread 5/6/4, 4 kinds per lesson. Math + strict + track-scope audits green.

## Batch S — shipped

Six more thin math lessons expanded to 15 verified items each (spread 5/6/4,
4 kinds per lesson), all CAS-verified with 0 rejections:

- `linear_regression_least_squares` (statistics) — means, least-squares slope
  via $\sum(x-\bar x)(y-\bar y)/\sum(x-\bar x)^2$, intercept $\bar y-b\bar x$,
  residuals, prediction, centroid property.
- `discrete_distributions_binomial_poisson` (statistics) — binomial mean/variance
  $np$, $np(1-p)$; binomial & Poisson PMFs via `binomial`, `exp`, `factorial`;
  $P(X\ge 1)=1-(1-p)^n$.
- `distributions` (probability) — expected value $\sum x_iP(x_i)$, variance
  $E[X^2]-(E[X])^2$, standard deviation, fair-die/two-dice/Bernoulli examples,
  pdf-area/probability-axiom conceptual checks.
- `implicit_differentiation` (5pt/university) — circles/curves $y'=-x/y$, product
  & power terms, $e^y=x$, $\sin y=x$, quotient-form results; distinct from the
  Batch-R `derivatives_implicit` set (harder, more transcendental cases).
- `trigonometric_identities` (5pt) — Pythagorean/reciprocal/double-angle/
  sum-difference identities verified numerically at special angles via `truth`
  predicates; special-angle evaluations.
- `sampling_estimation` (statistics) — standard error $\sigma/\sqrt n$, 95%/99%
  margins ($1.96/2.576\,SE$), CI half-width, CLT & unbiasedness conceptual checks.

**Fixes during authoring:** `distributions` open-worked item duplicated a medium
item's stem (identical $E[X]$ distribution) → deduped to 14; changed to a distinct
distribution $\{2,4,6\}$ and re-baked to 15/15. Two Hebrew-in-math lint hits fixed
by moving Hebrew out of `$...$`: `distributions` q5 ($P(\text{זוגי})$) and a
pre-existing Batch-M carryover in `data_representation` q0 (relative-frequency
fraction with Hebrew `\text{}`). Corpus-wide math lint now **0/207**.

## Batch T — shipped

Six more thin math lessons expanded to 15 verified items each (spread 5/6/4,
4 kinds per lesson), all CAS-verified with 0 rejections:

- `continuity_discontinuity` (calculus1) — removable limits via factor-and-cancel
  $\tfrac{x^2-a^2}{x-a}\to 2a$, jump/infinite discontinuity identification,
  point of discontinuity of $1/(x-3)$.
- `differential_equations_intro` (calculus1/ODE) — separable IVPs
  $y'=f(x),\ y(x_0)=y_0$, exponential $y'=ky$, solution verification
  ($y=e^x\Rightarrow y'=y$; $y=\sin x\Rightarrow y''+y=0$), order/model concepts.
- `mathematical_induction` (5pt) — closed forms $\tfrac{n(n+1)}{2}$, sum of odds
  $n^2$, sum of squares $\tfrac{n(n+1)(2n+1)}{6}$, sum of cubes
  $\left(\tfrac{n(n+1)}{2}\right)^2$ (verified numerically), base-case/inductive-step
  structure.
- `euclidean_geometry_circles` (4pt/5pt) — inscribed/central angle
  ($\theta_{\text{insc}}=\tfrac12\theta_{\text{cent}}$), Thales, equal tangents,
  cyclic-quadrilateral supplementary angles, intersecting-chords and
  tangent-secant power-of-a-point.
- `statistics_inference` (statistics) — $z=\tfrac{x-\mu}{\sigma}$ both directions,
  $x=\mu+z\sigma$, the 68–95–99.7 empirical rule, standard-normal facts.
- `power_series_radius` (calculus1/analysis) — radius via the ratio test
  $R=\lim|a_n/a_{n+1}|$ for $\sum x^n/b^n$ ($R=b$) and $\sum b^n x^n$ ($R=1/b$),
  center-shift invariance, endpoint/absolute-convergence concepts.

All 15/15 on first pass — no collisions or lint hits. Corpus math lint 0/207.

## Batch U — shipped

Six more thin math lessons expanded to 15 verified items each (spread 5/6/4,
4 kinds per lesson), all CAS-verified with 0 rejections:

- `chi_square_tests` (statistics) — cell contributions $\tfrac{(O-E)^2}{E}$,
  goodness-of-fit & contingency degrees of freedom ($k-1$, $(r-1)(c-1)$),
  expected count $\tfrac{RC}{N}$, non-negativity.
- `anova_one_way` (statistics) — grand mean, between/within/total df,
  $SSB=n\sum(\bar x_i-\bar x)^2$, mean squares, $F=MSB/MSW$, variance partition
  $SST=SSB+SSW$.
- `triangles_congruence` (3pt/4pt/5pt) — SSS/SAS/ASA/AAS criteria vs invalid AAA,
  corresponding-parts equality (sides/angles/perimeter/area), angle-sum
  ($180^\circ$), isosceles/equilateral angles.
- `matrix_representation` (linear algebra) — matrix-vector products component by
  component (identity, scaling, swap, shear), columns as basis images,
  composition = matrix multiplication.
- `orthogonal_matrices` (linear algebra) — dot products / orthogonality, norms,
  $|\det Q|=1$, $Q^TQ=I$, $Q^{-1}=Q^T$, rotation-matrix determinant
  $\cos^2\theta+\sin^2\theta$, length preservation.
- `spatial_reasoning` (3pt) — cube/box volume & surface area, faces/edges/vertices,
  cross-sections & nets, cylinder volume ($\pi r^2h$), cube space diagonal
  $s\sqrt3$.

**Fix during authoring:** the `spatial_reasoning` open-worked box-volume item
duplicated the medium $2\times3\times4$ item → deduped to 14; changed the worked
example to a $3\times4\times5$ box ($V=60$) and re-baked to 15/15. Corpus math
lint 0/207.

## Batch W — shipped (physics begins)

With the math corpus complete, work moved to **HS physics** (55 thin lessons, all
at 8q). Batch W expanded the HS mechanics core to 15 verified items each (spread
5/6/4, 4 kinds), all CAS-verified (SymPy arithmetic) with 0 rejections and 15/15
on first pass. All use $g=10\,\text{m/s}^2$ stated in-stem for clean answers:

- `kinematics_1d` — $v=u+at$, $s=ut+\tfrac12at^2$, $v^2=u^2+2as$, free fall,
  average speed, v-t graph slope, stopping distance/time.
- `newton_laws` — $F=ma$, weight $W=mg$, net force, perpendicular resultant,
  elevator normal force, friction $f=\mu N$, the newton unit, 3rd law.
- `work_energy` — $W=Fd\cos\theta$, $KE=\tfrac12mv^2$, $PE=mgh$, power $P=W/t=Fv$,
  work-energy theorem, energy conservation $v=\sqrt{2gh}$.
- `momentum` — $p=mv$, impulse $J=Ft=\Delta p$, elastic vs inelastic, perfectly
  inelastic common velocity, recoil, units.
- `projectile_motion` — independent H/V motion, $x=v_xt$, $t=\sqrt{2h/g}$,
  max height $v_y^2/2g$, horizontal-launch range, component $v\sin\theta$, parabola.
- `circular_motion` — $a=v^2/r$, $F=mv^2/r$, $\omega=v/r$, $v=\omega r$, period
  $T=2\pi r/v$, circumference, center-directed net force.

**Note on gating:** physics lessons carry `math_track: []` and render with
`learnerLevel=null`, so the quiz-panel filter (which only hides items whose
`points_level_min` exceeds the learner track) shows every physics item to all
learners — verified against `lesson-quiz-panel.tsx`.

## Batch X — shipped (physics mechanics II)

Continued physics expansion (49 thin remaining after W). Batch X took the next
mechanics cluster to 15 verified items each (spread 5/6/4, 4 kinds), all
CAS-verified with 0 rejections, 15/15 first pass, lint 0/207:

- `gravitation` — $W=mg$, inverse-square scaling, gravitational field $g=F/m$,
  planet/Moon weight, mass-product scaling, radius scaling.
- `friction` — $f=\mu N$, $f=\mu mg$, coefficient $\mu=f/N$, static vs kinetic,
  net force with friction, $a=(F-f)/m$, deceleration $a=\mu g$.
- `conservation_energy` — $PE=mgh$, $KE=\tfrac12mv^2$, $v=\sqrt{2gh}$,
  $h=v^2/2g$, total mechanical energy, pendulum drop.
- `static_equilibrium` — $\sum F=0$ & $\sum\tau=0$, tension, torque balance,
  shared supports, seesaw, couples.
- `torque` — $\tau=rF\sin\theta$, distance from torque, net torque, wrench,
  angled-force cases (30°/60°), units.
- `vectors_basics` — magnitude 2D/3D, components $v\cos\theta$/$v\sin\theta$,
  dot product, perpendicular resultant, scalar vs vector.

## Batch Y — shipped (physics waves & rotation)

Third physics cluster to 15 verified items each (spread 5/6/4, 4 kinds), all
CAS-verified, 0 rejections, 15/15 first pass, lint 0/207:

- `waves_basics` — $v=f\lambda$, $T=1/f$, $f=1/T$, wave count $n=ft$.
- `sound_waves` — longitudinal nature, speed in air, echo $d=vt/2$, pitch.
- `simple_harmonic_motion` — $F=-kx$, $\omega=\sqrt{k/m}$, $T=2\pi\sqrt{m/k}$,
  $v_{\max}=\omega A$, $a_{\max}=\omega^2A$.
- `harmonic_oscillation` — pendulum $T=2\pi\sqrt{L/g}$, spring energy $\tfrac12kA^2$,
  oscillation count.
- `rotational_kinematics` — $\omega=\theta/t$, $\alpha=\Delta\omega/t$,
  $v=\omega r$, $\omega=\omega_i+\alpha t$, $\omega^2=2\alpha\theta$, rev→rad.
- `rotational_dynamics` — $\tau=I\alpha$, $I=mr^2$, $L=I\omega$, disk inertia
  $\tfrac12mr^2$, rotational KE $\tfrac12I\omega^2$.

## Batch Z — shipped (physics electricity)

Fourth physics cluster to 15 verified items each (spread 5/6/4, 4 kinds), all
CAS-verified, 0 rejections, lint 0/207. Coulomb/field/potential items use
$k=9\times10^9$ with charges as exact `10**-6` rationals (no float drift):

- `electrostatics` — like/unlike charges, charge conservation, inverse-square
  force scaling.
- `electrostatics_coulomb` — $F=kq_1q_2/r^2$ explicit + scaling, Coulomb constant.
- `electric_field` — $E=F/q$, $F=qE$, $E=kQ/r^2$, conductor interior, N/C unit.
- `electric_potential` — $W=qV$, $V=kQ/r$, $V=Ed$, volt = J/C, $1/r$ scaling.
- `electric_circuits` — $V=IR$, $P=VI$, $P=I^2R$, $P=V^2/R$, series/parallel,
  energy $E=Pt$.
- `capacitors_dielectrics` — $Q=CV$, $C=Q/V$, $E=\tfrac12CV^2$, parallel/series
  combination, dielectric effect.

## Batch AA — shipped (physics magnetism/optics/2D motion)

Fifth physics cluster to 15 verified items each (spread 5/6/4, 4 kinds), all
CAS-verified, 0 rejections, lint 0/207:

- `magnetism` — $F=BIL$, $F=qvB$, $B=F/(IL)$, tesla unit, stationary-charge case.
- `electromagnetic_induction` — $\varepsilon=BLv$, $\varepsilon=\Delta\Phi/\Delta t$,
  $\varepsilon=N\Delta\Phi/\Delta t$, $\Phi=BA$, Faraday/Lenz, weber unit.
- `optics_geometric` — thin lens/mirror $\tfrac1f=\tfrac1{d_o}+\tfrac1{d_i}$,
  magnification $m=-d_i/d_o$, plane-mirror symmetry.
- `kinematics_2d` — independent H/V motion, $x=v_xt$, $t=\sqrt{2h/g}$, resultant
  speed, $H=v_y^2/2g$, component $v\cos\theta$.
- `vectors_kinematics_2d_3d` — 2D/3D magnitude, dot product, components,
  scalar vs vector, perpendicular resultant.
- `collisions` — $p=mv$, momentum conservation, perfectly-inelastic common
  velocity, impulse $J=m\Delta v$, elastic-KE fact.

## Batch V — shipped (math corpus complete)

The final six thin math lessons expanded to 15 verified items each (spread 5/6/4,
4 kinds per lesson), all CAS-verified with 0 rejections and 15/15 on first pass:

- `function_investigation_uni` (5pt/university) — critical points ($f'=0$),
  extrema values, inflection ($f''=0$), second-derivative test, vertex analysis.
- `multivariable_limits` (calculus2) — limits of polynomials/roots/exponentials by
  substitution, path test for non-existence, continuity condition.
- `limits_epsilon_delta` (5pt/university) — for linear $f$, $\delta=\varepsilon/|m|$
  across a range of slopes and tolerances; the formal implication.
- `la_orthogonality` (linear algebra) — dot products & orthogonality, norms,
  projection coefficient $\tfrac{a\cdot b}{b\cdot b}$, orthonormal sets,
  independence of orthogonal vectors.
- `linear_transformations_kernel_image` (linear algebra) — rank-nullity
  $\dim\ker+\operatorname{rank}=n$ across injective/surjective/zero maps, kernel &
  image definitions.
- `continuity_uniform` (calculus1/analysis) — Lipschitz $\delta=\varepsilon/L$,
  uniform ⇒ continuous, Heine–Cantor, $x^2$ non-uniformity, Lipschitz bound.

**Milestone:** `_scan_thin_math.mjs` now reports **0 thin math lessons** — every
math lesson in the corpus has a 15+ verified, calibrated (30/40/30), 4-kind,
bilingual question bank. Corpus math lint 0/207.

## Corpus progress

Verified 15+ item banks now cover **all 120 math lessons** (Batches B, D, E, F, G, H,
I, J, K, L, M, N, O, P, Q, R, S, T, U, V + exponents): the entire 3pt/4pt algebra & functions foundation
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

## Batches W–KK — shipped (physics + makhina + university complete)

After the math corpus hit 15+ everywhere, the same proven depth+verify pipeline
was fanned out across the rest of the corpus, six lessons per batch, all
SymPy-verified (0 rejections) and math-lint clean:

- **W–AA (HS physics):** mechanics core, gravitation/friction/energy/static-eq/
  torque/vectors, waves/sound/SHM/rotational, the electrostatics cluster,
  magnetism/induction/optics/2D-kinematics.
- **BB–EE (HS + advanced physics):** units/fluids/angular-momentum/COM/doppler,
  Gauss/Kirchhoff/AC/Biot-Savart/Ampère/torque-equilibrium, relativity/modern/
  nuclear/induction/EM-waves/atomic, Maxwell/physical-optics/interference/
  rigid-body/angular-momentum/COM.
- **FF–GG (makhina):** calculus-intro, functions, trigonometry, mechanics,
  energy-work, waves-sound, electricity, thermodynamics, plus the university
  calculus foundations (derivatives-intro, antiderivatives, definite-integral-area,
  function-basics).
- **HH (calculus_1):** integration-by-parts, integration-substitution, L'Hôpital,
  mean-value-theorem, optimization-problems, absolute-extrema.
- **II (calculus_1 + statistics):** number-sets-review, taylor-formula,
  series-convergence-tests, series-convergence-advanced, probability-basic,
  random-variables.
- **JJ (statistics + linear algebra):** confidence-intervals, hypothesis-testing,
  la-vectors, la-matrices, la-determinants, la-vector-spaces.
- **KK (linear algebra):** la-eigenvalues, la-diagonalization,
  inner-product-gram-schmidt, linear-systems-gaussian-elimination,
  vector-spaces-basis-dimension.

**MILESTONE — corpus complete:** every lesson across the whole platform (math,
HS physics, makhina math+physics, university calculus/linear-algebra/statistics)
now has a 15+ item, calibrated (~30/40/30), 4–5-kind, bilingual, SymPy-verified
question bank. A full scan reports **0 thin lessons (<15 q) across all 207 lesson
files**, and math lint is clean (0/207 issues).

## MILESTONE — per-track visibility invariant (this window)

Beyond raw counts, closed the gap where a *served track* could see fewer than 15
questions because higher-track items were gated away:

- `sequences_geometric` 3pt: 11 → **15** visible (+4 finite-sequence items; the 4
  infinite-series items stay correctly 4pt-gated). Total 19.
- `inequalities` 3pt: 10 → **15** visible (+5 linear-inequality items; the 5
  quadratic-inequality items stay 4pt-gated). Total 20.
- `integrals_applications` 4pt: 14 → **15** visible (+1 area item; the
  volume-of-revolution item stays 5pt-gated). Total 16.

Corpus-wide sweep now reports **0 served tracks below 15 visible items** in any
lesson. Shipped and reseeded to production (run 29676280700, success; live smoke
200 on `/`, `/learn`, `/sign-in`).

## Original-complaint audit (all resolved corpus-wide)

Automated re-verification against the user's six original complaints:

1. **Level + type diversity** — 0/207 lessons have <3 question kinds; 0/207 have
   a degenerate difficulty spread (no missing easy/hard, no >55% hard / >65% easy).
2. **Conceptual depth** — avg 2968 section words/lesson; why_matters on 207/207.
3. **Math notation** — KaTeX/Hebrew-in-math lint: 0 issues across 207 files.
4. **One-line solutions** — every baked item carries multi-step bilingual working.
5. **Repeated questions in answer areas** — 0 duplicate stems within a lesson; 0
   question stems duplicated from a worked_example.
6. **Wrong-answer marking** — 3116/3116 baked items were CAS-verified at bake time
   (0 rejected, 0 `needs_review` shipped as graded).

## Reseed operational note

The `Seed DB (one-shot)` workflow only seeds lessons/questions to Neon under
**`target=lessons-from-json`**; the default `all` target runs the Neo4j KG step
(currently failing on Aura DNS) and *skips* the lesson seed. Always dispatch
content reseeds with `-f target=lessons-from-json`.

## Pending (not yet done this window)

- **Within-lesson 5pt tags:** in mixed 4pt/5pt lessons (integrals_applications
  volumes/shells, derivatives_applications related-rates) raise 5pt-only items
  with `_pl(..., "5pt")` so 4pt learners don't see 5pt-only work.
- **Within-lesson 5pt tags:** in mixed 4pt/5pt lessons (integrals_applications
  volumes/shells, derivatives_applications related-rates) raise 5pt-only items
  with `_pl(..., "5pt")` so 4pt learners don't see 5pt-only work.
- **Full theory rewrites** (Q14) for the corpus.
- **Variants** where MoE depth genuinely differs (rarer than first estimated —
  most shared concepts only need per-item tagging, handled by the base fix).
- **Membership prunes** of out-of-scope concepts from track categories.
- **Non-symbolic strands** (geometry proofs, word problems, probability):
  author + `needs_review`, defer from graded.
