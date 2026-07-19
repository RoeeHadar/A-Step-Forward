# Lesson Rewrite — Scope Map & Variant Plan (Math first)

**Status:** living document · **Started:** 2026-07-19 · **Owner:** curriculum + math-notation agents
**Mandate:** rewrite ALL lessons to full, level-appropriate depth with high-volume,
high-variance, verified exercises. Grilling decisions log: this file's sibling in the
2026-07-19 session summary.

This is the "scope report" the rewrite mandate requires. It records, per track, what
is IN scope, what is pruned (and why), what is added, and which concepts get per-track
**variant lessons**. It is the authoritative input to authoring; every prune/add is a
best-judgment call cross-checked against the MoE Bagrut syllabus + `research/bagrut_math_research.md`
+ `apps/web/src/lib/curriculum-categories.ts`.

---

## 1. Decisions locked (from grilling session)

1. **Per-track variant lessons** — `<concept>__3pt` / `__4pt` / `__5pt`, created ONLY
   where MoE scope/depth/explanation genuinely differ; a single shared file where a
   topic is taught identically across levels.
2. **Canonical `concept_id`** — KG / mastery / prereqs stay level-agnostic. A variant
   file is `id: <concept>__<track>` but carries `concept_id: <concept>`. Mastery never
   fragments; only the lesson/reader layer is track-aware.
3. **MoE syllabus is scope authority**, reconciled with `curriculum-categories.ts`.
4. **Depth bar (per-lesson floors, not corpus averages):** intro + ≥3 theory sections
   (~300+ EN words each, HE parity ≥90%) + ≥4 worked examples (≥1 graphical, ≥1
   creative/parametric) + pitfalls/edge-cases + method_guide + why_matters +
   before_exam + summary; ≥25 questions across ≥6 kinds with calibrated easy/medium/hard
   spread; every question a multi-step bilingual explanation (no one-liners).
5. **Facet-coverage gate** — each concept×track has a coverage map (facets + question
   archetypes); the lesson must hit every mapped facet (section + questions) or a
   companion lesson does. Enforced by a new strict audit.
6. **Sourcing:** blueprint-only from Geva/Goren (structure + archetype patterns, derived
   from public ToCs + reputable prep sources), all problems authored original; MoE exam
   PDFs (`apps/web/public/content/bagrut/`) for verbatim-safe calibration. MoE = ground truth.
7. **Verification:** two-tier — deterministically-checkable items machine re-derived and
   must match the key (build fails otherwise); non-verifiable items get full worked
   solutions + `needs_review`.
8. **Routing:** catalog auto-selects the learner's track variant; advanced variant
   reachable via link; unknown level → most foundational variant. Basics exist in every track.
9. **Order:** HS Bagrut math → HS physics → makhina → university. Ship batch-by-batch.

---

## 2. Question-archetype taxonomy (applies to every math concept)

Each concept×track coverage map draws its mandatory archetypes from this universe.
A lesson must include the archetypes marked required for its track.

| Archetype | What it tests | 3pt | 4pt | 5pt |
|-----------|---------------|-----|-----|-----|
| Procedural fluency | Direct computation (solve, evaluate, differentiate) | ✅ | ✅ | ✅ |
| Conceptual / verbal (נמק) | Explain why; justify a claim in words | ✅ | ✅ | ✅ |
| Graphical / multi-representation | Read/sketch graphs; sketch `1/f(x)`, `f(x)+c`, `|f(x)|`, `f'`; match graph to formula | ✅ | ✅ | ✅ |
| Parametric / existence | "For which `k`…", "how many solutions", `y=k` intersections, parameter ranges | ○ | ✅ | ✅ |
| Connections to adjacent concepts | function↔derivative↔slope↔area; sequence↔exp; prob↔combinatorics | ○ | ✅ | ✅ |
| Reverse / inverse | Given the answer/graph, find the input/function/parameter | ○ | ✅ | ✅ |
| Error analysis | "Find the mistake"; classify a wrong solution | ○ | ✅ | ✅ |
| Real-world modeling (word) | Motion, purchase, growth/decay, optimization in context | ✅ | ✅ | ✅ |
| Proof / justification | 3pt: 1–3 sentence explanation · 4pt: cite theorem/formula · 5pt: full deductive chain | (light) | ✅ | ✅ (heavy) |

✅ required · ○ include where the MoE topic supports it.

Worked-example set per lesson must span: 1 easy procedural, 1 medium multi-step, 1
graphical/multi-representation, 1 exam-level parametric/creative (4pt/5pt) or word (3pt).

---

## 3. MATH scope by track (IN / PRUNE / ADD)

Legend: **IN** = author to full bar for this track · **PRUNE** = remove from this
track (belongs elsewhere / not in MoE for this level) · **ADD** = missing, author new.

### 3.1 — 3 units (172 / 371 / 372, new curriculum primary; 182/381/382 legacy)

**IN (new track, taught at 3pt register — concrete, numeric, minimal abstraction):**
graph reading; descriptive statistics; simple + basic conditional probability (tree,
without replacement); percentages & financial (markup/discount chains, simple/compound
interest); linear & quadratic equations and systems; linear/quadratic/exponential
functions (read + basic manipulation, transformations); arithmetic & geometric sequences
(growth/decay); right-triangle trigonometry + plane trig (sine/cosine law, basic);
similar triangles & basic Euclidean geometry; analytic geometry basics (distance,
midpoint, line); **linear programming (372)**; **quadratic modeling (372)**; spatial
reasoning & 3D volumes of standard solids (prism, cylinder, cone, sphere) via direct
formulas; normal distribution (read the curve, empirical rule — `normal_distribution_basics`).

**PRUNE from 3pt:**
- **Calculus** (derivatives/integrals) — removed from new 372. Keep `derivatives_intro`,
  `derivatives_rules`, `integrals_intro`, `limits_4pt` as **old-382 legacy only**, clearly
  flagged; do NOT surface to a new-track 3pt learner by default.
- **Cavalieri's principle** — NOT 3pt. 3pt volumes use direct formulas only. If a shared
  volumes lesson mentions Cavalieri, the 3pt variant omits it.
- Formal proofs (full deductive) — 3pt does "explain", not `הוכח` chains.
- Any parameter-heavy investigation, conditional-Bayes, binomial.

**ADD / author for 3pt:** dedicated 3pt variants of shared topics (see §4), a proper
`linear_programming` lesson to the new bar, `quadratic_model_fitting` expanded to
exam-style, 3pt-level `spatial_reasoning`/`3d_solids_volume` (formula-based, no Cavalieri).

### 3.2 — 4 units (471 / 472; 481/482 legacy)

**IN:** everything a 4pt learner needs, taught with more abstraction than 3pt:
full derivative rules (power, product, quotient, chain); rational & root-function
investigation (domain, asymptotes, extrema, monotonicity, sketch); integration
(polynomial, simple rational, `∫e^{ax}`, `∫sin(ax)`), area between curves, basic volume;
exp/log functions & calculus, logarithmic equations; continuous growth/decay `A=A₀e^{kt}`;
basic trig identities (`sin²+cos²=1`, double angle as used in calc), trig in space;
sequences (arith+geom, finite/infinite sums); analytic geometry (line, circle, tangent);
conditional & independent probability, multi-stage trees; descriptive stats,
`normal_distribution_z_scores`, linear regression/correlation, intro hypothesis testing (472);
plane vectors (472 new); Euclidean proofs (cite theorem level).

**PRUNE from 4pt:**
- Complex numbers, mathematical induction, binomial/Bernoulli distribution — **5pt only**.
- Volume of revolution (full) — 5pt; 4pt gets only `volumes_of_revolution_basic`.
- Integration by substitution (general), implicit differentiation, related rates — 5pt.
- ε–δ limits, differential equations — university/makhina, never 4pt.

**ADD:** `hypothesis_testing_intro` to bar; ensure `vectors_plane`/`vectors_2d` 4pt variant.

### 3.3 — 5 units (571 / 572; 581/582 legacy)

**IN (all 4pt topics at higher depth + 5pt-exclusive):** full function investigation
with second derivative (inflection, concavity), parameter-heavy graph matching;
optimization (geometry/context) + constraint setup; **mathematical induction**;
**binomial / Bernoulli** probability, conditional-Bayes; **complex numbers** (arithmetic,
polar, De Moivre, n-th roots, geometric locus in the Gauss plane); full trig identity set
(addition, double/half angle) + trig equations + trig calculus; **3D vectors** (dot
product, projections); advanced integration (**substitution**), **volume of revolution**;
sequences (infinite geometric, recursion, induction link); formal Euclidean proof chains
(circles, cyclic quads, tangents); exp/log full investigation (572); conics (572 new).

**PRUNE from 5pt (the user's explicit examples):**
- **ε–δ (epsilon–delta) limits** — NOT HS 5pt. `limits_5pt` uses intuitive/one-sided
  limits and standard limits (`sin u/u`), NOT the formal ε–δ definition. ε–δ lives in
  `limits_epsilon_delta` (makhina / calculus_1) only.
- **Differential equations** — university/makhina only; never in a 5pt HS lesson.
- Multivariable, partial derivatives, series convergence tests, integration by parts /
  partial fractions — university (calc1/2), not 5pt HS.

**ADD:** ensure a real `mathematical_induction`, `complex_numbers_5pt`,
`analytic_geometry_conics`, `distributions` (binomial) at the 5pt bar; 5pt learners also
need **foundational** lessons (basics exist in every track — see §4.2).

---

## 4. Variant plan

### 4.1 Concepts that GET per-track variants (scope/depth/register genuinely differ)

These shared `concept_id`s are taught across ≥2 tracks with materially different scope,
so each served track gets its own deep variant file (`<concept>__<track>`):

| concept_id | 3pt | 4pt | 5pt | Why variants differ |
|------------|-----|-----|-----|---------------------|
| `functions_quadratic` | ✅ | ✅ | ✅ | 3pt: vertex/roots/graph; 4pt: +parameter, intersections; 5pt: +full investigation links |
| `sequences_geometric` | ✅ | ✅ | ✅ | 3pt: growth/decay numeric; 4pt: finite/infinite sums; 5pt: recursion + induction link |
| `trigonometry_ratios` / plane | ✅ | ✅ | ✅ | 3pt: right triangle; 4pt: sine/cosine law + space; 5pt: identities/equations/calc |
| `analytic_geometry` | ○(basic) | ✅ | ✅ | 3pt: distance/line; 4pt: circle+tangent; 5pt: conics+locus |
| `probability_*` | ✅ | ✅ | ✅ | 3pt: simple/tree; 4pt: conditional/Bayes; 5pt: binomial/Bernoulli |
| `derivatives_*` | ✗(legacy 382) | ✅ | ✅ | 4pt: poly/rational rules; 5pt: trig/exp + implicit + related rates |
| `integrals_*` | ✗ | ✅(basic+area) | ✅ | 5pt adds substitution + volume of revolution |
| `function_analysis_*` | ✗ | ✅ | ✅ | 4pt: extrema/monotonicity; 5pt: +second derivative/inflection/parameter |
| `vectors_*` | ✗ | ✅(2D, 472) | ✅ | 5pt adds 3D + dot product/projection |
| `3d_solids_volume` | ✅ | ✅ | ○ | 3pt: direct formulas (NO Cavalieri); 4pt+: with proof/derivation |

(`✅` served & variant · `○` marginal · `✗` not served / legacy only.)

### 4.2 "Basics in every track" — 5pt/4pt foundational coverage

5pt and 4pt learners still need the foundational lessons (algebra, functions intro,
basic trig, sequences basics). These are served to higher tracks via the shared
foundational file (no separate variant needed unless the register differs). The catalog
must include foundational concepts in the 4pt/5pt learner path, not only advanced ones.

### 4.3 Concepts that stay SINGLE file (taught identically or single-track)

Pure-foundation (`algebra_basics`, `factoring`, `exponents`, `arithmetic`,
`fractions_algebraic`, `word_problems`), and single-track/university concepts
(`limits_epsilon_delta`, `complex_numbers_5pt`, `mathematical_induction`, all `uni_*`,
`la_*`, `calc*`) keep one file.

---

## 5. Deprecated / legacy handling

- Old-track-only calculus at 3pt (`derivatives_intro/rules`, `integrals_intro`,
  `limits_4pt` under 372) → keep, flag `old_track_only`, never default-serve to new-track
  3pt learners. Add a `curriculum_track: old|new|both` note in authoring.
- 481/581 old chapter structure mocks are legacy; new-track (471/571) is primary.

---

## 6. Sequencing (math batches)

1. **Functions & calculus family** (where the user's examples came from): `functions_*`,
   `derivatives_*`, `function_analysis_*`, `integrals_*`, `optimization_*`,
   `limits_*` — 4pt + 5pt variants first (largest exam weight), then 3pt function lessons.
2. **Algebra & sequences**: `algebra_basics`, `equations_*`, `sequences_*`, `logarithms`,
   `exponential_*`.
3. **Geometry & trig**: `trigonometry_*`, `analytic_geometry_*`, `circles`,
   `triangles_congruence`, `quadrilaterals`, `vectors_*`.
4. **Probability & statistics**: `probability_*`, `*_statistics`, `distributions`,
   `normal_distribution_*`, `linear_regression_*`, `hypothesis_testing_*`, `combinatorics_*`.
5. **5pt-exclusive**: `mathematical_induction`, `complex_numbers_*`, `analytic_geometry_conics`.
6. **3pt-new-track**: `linear_programming`, `quadratic_model_fitting`, `spatial_reasoning`.

Then HS physics → makhina → university (separate scope sections to be appended when reached).

---

## 7. Prune/add change log (append as authored)

| Date | concept×track | Action | Rationale |
|------|---------------|--------|-----------|
| 2026-07-19 | `limits_5pt` | PRUNE ε–δ | Not HS 5pt; ε–δ is makhina/calc1 (`limits_epsilon_delta`) |
| 2026-07-19 | 3pt volumes | PRUNE Cavalieri | 3pt uses direct volume formulas only |
| 2026-07-19 | 4pt calculus | PRUNE substitution/impl./related-rates/volume-of-rev | 5pt-only per MoE |
| 2026-07-19 | 5pt | PRUNE differential equations, multivariable, series tests | university-only |
