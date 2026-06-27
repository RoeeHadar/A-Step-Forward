# Israeli Bagrut Mathematics — Per-Level Depth Guide

> **Agent reference document.** All tutors, curriculum designers, and quiz builders must read
> this before generating or adapting content for a learner. Keep in sync with
> `content/knowledge-graph/math-high-school.yaml` and `curriculum-categories.ts`.

---

## Two Parallel Programs (critical!)

Israel has two simultaneous Bagrut tracks. Always ask which program the student follows.

| Track | Legacy program (pre-2023 entry) | New program (entered HS from Sept 2023) |
|-------|--------------------------------|----------------------------------------|
| 3 units | 801 · 802 · 803 | 172 · 371 · 372 |
| 4 units | 484 · 485 | 471 · 472 |
| 5 units | 581 · 807 | 581 · 582 |

**Inheritance rule:** 4pt ⊃ 3pt core; 5pt ⊃ 4pt core. Higher levels add depth; topics are rarely removed.

### What the new program removes from 3pt:
- **Sequences** (arithmetic + geometric) — fully removed from 372.
- **Derivatives and integrals** — removed (were in legacy 803 as a stripped calculus unit).
- **Circle analytic geometry** — removed from 372; more spatial reasoning instead.
- **3D trig** — replaced by volume/area applications.

---

## Concept-by-concept breakdown

### `functions_quadratic` — Parabola / Quadratic Functions

**3pt (801/802 / legacy; 372/371 / new)**
- Opening direction from sign of $a$; axis of symmetry; vertex $(h, k)$ via $h=-b/(2a)$
- $x$-intercepts (factoring or quadratic formula); $y$-intercept $= c$
- Increasing/decreasing relative to vertex — **no derivative**
- Positive/negative domains
- Parabola ↔ line intersection (substitute → quadratic)
- Optimization by vertex (max revenue/profit word problems)
- **NOT required:** completing the square, parametric analysis, conics
- Sketch from 3 points (vertex + intercepts)

**4pt adds:**
- Parametric parabolas: conditions on $k$ for number of intersections with a line
- Quadratic inequalities (sign chart)
- Systems: line + parabola with existence analysis

**5pt adds:**
- Parabola inside full calculus investigation (חקירה מלאה)
- Function transformations: $|f(x)|$, shifts
- Conic treatment (807/582): $y^2 = 4px$, focus/directrix
- Tangent line via $f'(x_0)$; relationship between $f$, $f'$, $f''$ graphs

---

### `equations_quadratic` — Quadratic Equations

**3pt**
- Solve by factoring (common factor, trinomial, difference of squares)
- Quadratic formula; discriminant $\Delta$ → 0/1/2 real solutions
- Simple word problems → quadratic setup
- Biquadratic substitution ($t = x^2$)
- Systems: one linear + one quadratic

**4pt adds:**
- Parametric: "for which $k$ does $x^2 + kx + 9 = 0$ have two solutions?"
- Quadratic inequalities (sign chart / number line)
- Rational equations → quadratic after clearing denominators

**5pt adds:**
- Absolute value and radical quadratics
- Quadratics inside trig equations ($t = \sin x$)
- Systems with conics (line + circle → quadratic in $x$)

---

### `sequences_arithmetic` — Arithmetic & Geometric Sequences

> ⚠️ **Removed from new 3pt program (372).** Only present for legacy 3pt (801/802) and 4pt+.

**3pt legacy (801/802)**
- Common difference $d$; $a_n = a_1 + (n-1)d$
- $S_n = n/2 \cdot (a_1 + a_n)$
- Find $n$, $a_1$, $d$ from two conditions
- Insert numbers between endpoints; count integers in range
- Word problems (seats, prizes, consecutive integers)

**4pt adds:**
- Geometric sequences alongside arithmetic
- Infinite geometric series $S_\infty = a_1/(1-q)$ when $|q|<1$
- Mixed arithmetic + geometric word problems
- Growth/decay as geometric (compound interest, half-life)

**5pt adds:**
- Sequences in harder algebra systems
- Connection to limits ($\lim_{n\to\infty}$ of geometric)
- Mathematical induction proof of sequence formulas

---

### `trigonometry_ratios` — Trigonometry

**3pt**
- SOH-CAH-TOA in right triangles only
- Special angles: $30°, 45°, 60°$ exact values
- Applications: height/distance, angle of elevation/depression
- **802 adds:** sine rule, cosine rule, area $= \frac{1}{2}ab\sin C$ (oblique triangles)
- **Legacy 802 adds:** 3D trig — box, pyramid
- **New 371:** plane trig only; 3D removed

**4pt adds:**
- Sine/cosine rules in coordinate geometry proofs
- Trig in circle geometry (inscribed angles)

**5pt adds** (separate KG nodes: `trigonometry_identities`, `trigonometry_equations`):
- Unit circle definition for all angles; radians
- Sum/difference, double-angle identities
- Trig equations: $\sin x = k$, $\cos(2x) = k$, quadratic-in-$\sin x$
- $\sin x, \cos x, \tan x$ as full functions with domain, period, asymptotes
- Derivatives: $(\sin x)' = \cos x$, $(\cos x)' = -\sin x$
- Investigation of $a\sin(bx+c)+d$

---

### `analytic_geometry` / `analytic_geometry_basic`

**3pt**
- Distance formula; midpoint formula; slope; line forms ($y=mx+b$, $ax+by+c=0$)
- Parallel ($m_1=m_2$), perpendicular ($m_1 m_2=-1$)
- Intersection of two lines
- Area of polygon via coordinate decomposition
- **Legacy 803:** circle $(x-a)^2+(y-b)^2=r^2$; tangent; line–circle intersection
- **New 372:** circle removed; more spatial reasoning / area

**4pt adds:**
- Coordinate geometry proofs of quadrilateral properties
- Combined with Euclidean geometry in exam questions

**5pt adds** (807/582):
- Loci
- Ellipse $x^2/a^2 + y^2/b^2 = 1$ (overview)
- Parabola as conic
- Vectors $\vec{AB}$, dot product, angle between vectors
- 3D trigonometry with vectors (582)

---

### `probability_basic` — Probability

**3pt**
- Classical: $P(A) = \text{favorable}/\text{total}$
- Complement: $P(A^c) = 1 - P(A)$
- Tree diagrams (2 stages)
- Union of mutually exclusive events
- **802 adds:** dependent two-stage events; intro to normal distribution

**4pt adds:**
- Conditional probability $P(A|B) = P(A\cap B)/P(B)$
- Two-way contingency tables; independence
- Combinatorics: $nPr$, $nCr$, multiplication principle
- Inclusion-exclusion

**5pt adds** (node: `distributions`):
- Binomial: $P(X=k)=\binom{n}{k}p^k(1-p)^{n-k}$
- Normal distribution with z-scores
- Bayes-style multi-step problems
- Expected value

---

### `derivatives_intro` / `derivatives_rules` / `derivatives_applications`

> ⚠️ **Legacy 803 had a stripped 3pt calculus unit. New 372 removes it entirely.**
> In the repo, derivatives are tagged as `4pt/5pt` only — which is correct for new-program students.

**Legacy 3pt (803 only):**
- Power rule for polynomials: $(x^n)' = nx^{n-1}$
- Tangent line slope + equation $y - f(a) = f'(a)(x-a)$
- Find extrema: $f'(x)=0$; sign test intervals
- Full investigation of polynomial and rational functions
- Optimization via derivative
- **No limits, no product/quotient/chain rule**

**4pt (new 472):**
- Pre-calculus slope analysis
- Derivatives of $e^x$ and $\ln x$ for growth/decay contexts

**5pt (581 — guaranteed major exam question):**
- Limit definition (intuitive)
- All rules: product, quotient, **chain rule**
- $(e^x)' = e^x$; $(\ln x)' = 1/x$; $(\sin x)' = \cos x$; $(\cos x)' = -\sin x$
- Second derivative, concavity, inflection points
- Full חקירה מלאה (domain, asymptotes, monotonicity, extrema, concavity, sketch)
- Parametric investigation: "find $a$ such that $f$ has exactly one extremum"
- Optimization with geometric constraint (max area, min material)

---

### `definite_integrals` — Integrals

> ⚠️ **Legacy 803 had a stripped 3pt integral unit. New 372 removes it entirely.**

**Legacy 3pt (803):**
- Antiderivative of polynomials
- $\int_a^b f = F(b) - F(a)$
- Area under curve (polynomial, mostly above $x$-axis)
- Find $f(x)$ given $f'(x)$ and initial condition
- **No substitution, no trig integrals, no between-curve areas**

**4pt (472):**
- Integrals of $e^x$, $1/x$ in exponential/log chapter
- Basic area

**5pt (581 — appears every exam):**
- FTC, signed area, area below axis (absolute value trick)
- Area between two curves (split at intersection)
- $u$-substitution with limit change; $\int f'/f = \ln|f|$
- Accumulation from graph of $f'$
- Volumes of revolution around $x$-axis (582)

---

## Typical exam question distribution (past 5 years, 581)

| Chapter | % of exam marks | Always / Sometimes |
|---------|----------------|--------------------|
| Calculus (derivatives + investigation) | ~30% | Always |
| Integrals + area | ~20% | Always |
| Trigonometry | ~15% | Always |
| Probability + combinatorics | ~15% | Always |
| Analytic geometry / vectors | ~10% | Always |
| Sequences / series | ~5% | Sometimes |
| Algebra (systems, parameters) | ~5% | Sometimes |

---

## Agent usage notes

- Always resolve `learnerLevel` from `learner_profiles.points_group` before generating content.
- A `3pt` learner on the new program should **not** receive sequences, derivatives, or integral content.
- A `3pt` learner on the legacy program CAN receive stripped calculus (803 style) — check `onboarding.background_notes` for "old/new program" clues.
- When generating worked examples, use **simple integers** for 3pt, **messier fractions and parameters** for 5pt.
- The 5pt investigation (חקירה מלאה) is the single highest-value skill to practice for exam prep.

---

## Gool.co.il chapter mapping (legacy 3pt)

| Gool PDF | Content |
|----------|---------|
| **801** | Ch.2 Parabola+quadratics; Ch.3 Analytic geometry basics; Ch.8 Trig; Ch.9 Arithmetic sequences; Ch.7 Probability |
| **802** | Ch.2 Parabola graphs; Ch.3 Sequences (arith+geom); Ch.5 Trig; Ch.6 Trig in space; Ch.5 Probability; Ch.9 Normal distribution |
| **803** | Ch.2 Analytic geometry+**circle**; Ch.3–5 **Calculus** (poly/rational/root); Ch.6 Optimization; Ch.7 **Integrals** |

*Last updated: 2026-06-27. Cross-reference with `content/knowledge-graph/math-high-school.yaml` for KG-level granularity.*
