# Israeli Bagrut Mathematics Exam Research Report

**Purpose:** Calibrate lesson depth, build dependency trees, design mock exams, and identify stable vs. variable exam patterns.  
**Scope:** 3 / 4 / 5 יחידות לימוד (units of study), 2015–2024, with forward notes on the 2025–2026 new curriculum.  
**Sources:** Ministry of Education exam booklets (`meyda.education.gov.il`), official scoring keys, Yoel Geva / Melumad / BagrutOnline curriculum breakdowns, Wikipedia & Hamichlol exam structure summaries, and analysis of 18 consecutive 371 exams (Geva prep booklet, 2020–2024).

---

## Executive Summary

Israeli Bagrut math is **not one exam** but a **modular system** of 2–3 external questionnaires per point level, each with its own chapter structure, choice rules, and weight in the final grade. Two parallel curriculum tracks coexist through ~2026:

| Track | Entry cohort | 3pt codes | 4pt codes | 5pt codes |
|-------|--------------|-----------|-----------|-----------|
| **Old (תוכנית ישנה)** | Pre–Sept 2023 + external candidates | 182 / 381 / 382 | 481 / 482 | 581 / 582 |
| **New (תוכנית חדשה)** | Sept 2023+ high-school entrants | 172 / 371 / 372 | 471 / 472 | 571 / 572 |

**Stable patterns (both tracks, all years):**
- Non-graphing calculator + attached formula sheets (דפי נוסחאות) on all external papers.
- **Process grading is mandatory** — final answers without written steps risk score reduction or exam disqualification (טוהר הבחינות, Director-General Circular 9/ד).
- Multi-part questions (א–ד+) with escalating difficulty within each question.
- Heavy use of **word problems**, **parameter problems** (פרמטר), and **"justify / prove / explain"** sub-items (נמק, הוכח).
- Calculus questions at 4pt+ almost always combine investigation + sketch + area/volume.

**Variable patterns:**
- Point value per question (20 / 25 / 27 / 28 / 33.3) shifts by year and adapted-exam status.
- Number of questions required (4 vs. 5 of 8) changed on several papers post-2014 reform.
- New curriculum **reallocates topics** (e.g., 3pt removes full calculus; 5pt adds short-question blocks and induction).

---

## Critical Context: Two Curricula in Parallel

### Timeline

| Period | Dominant track | Notes |
|--------|----------------|-------|
| 2015–2022 | Old curriculum only in schools | Codes 182–582 |
| 2023 | Pilot new curriculum in select schools | Both tracks examined |
| Sept 2023+ | New curriculum mandatory for new HS entrants | 172–572 rollout |
| 2024–2026 | Both tracks examined | External candidates may choose old or new (4pt/5pt) |
| 2027+ | Old track expected to phase out | Verify with Ministry updates |

### Weighting of Questionnaires (Final External Grade)

| Level | Questionnaire | Old code | New code | Weight | Typical grade |
|-------|---------------|----------|----------|--------|---------------|
| **3pt** | First | 182 | 172 | 25% | י' |
| | Second | 381 | 371 | 35% | י"א |
| | Third | 382 | 372 | 40% | י"ב |
| **4pt** | First | 481 | 471 | 65% | י"א |
| | Second | 482 | 472 | 35% | י"ב |
| **5pt** | First | 581 | 571 | 60% | י"א |
| | Second | 582 | 572 | 40% | י"ב |

**Bonus points (מבחן בונוס):** +12.5 for 4pt, +25 for 5pt, if exam score ≥ 60.

---

## Universal Exam Rules (All Levels)

| Rule | Detail |
|------|--------|
| **Calculator** | Non-graphing only (מחשבון לא גרפי). Programmable/graphing features → disqualification |
| **Formula sheets** | Attached נספח with standard formulas; level-specific (3/4/5 יח"ל) |
| **Answer booklet** | Write question number only (not full question text); new page per question |
| **Grading** | Full written solution required even when using calculator; "lack of detail may reduce score or disqualify" |
| **Over-answering** | If student answers more than allowed, **only the first N answers in the booklet are graded** |
| **Partial credit** | Allowed on accumulation-style papers (3pt 172/371); chapter-constrained papers grade whole questions |
| **Proof standard** | Geometry: formal proofs (הוכח). Calculus: justify classification of extrema, asymptote identification, graph matching |

---

# Part 1: Three Units (3 יחידות לימוד)

## 1.1 Exam Structure

### Old Curriculum (182 / 381 / 382) — 2015–2024 primary track

| Questionnaire | Duration | Questions | Choice rule | Points | Weight |
|---------------|----------|-----------|-------------|--------|--------|
| **182** (first) | 1h 15m – 1h 30m | 6 | Accumulation: answer any combination up to **100 pts** (typically 4×25) | 25/q | 25% |
| **381** (second) | 1h 30m – 1h 45m | 6 | Same accumulation model | 25–27/q | 35% |
| **382** (third) | 2h – 2h 30m | 6 | **Choose exactly 4** of 6 (first 4 graded if more) | 25–28/q | 40% |

**382 choice rule (strict):** 4 of 6 questions → 4×25 = 100 (or 4×28 = 112 capped at 100 in some years).

### New Curriculum (172 / 371 / 372) — from 2024 exams

| Questionnaire | Duration | Questions | Choice rule | Points | Weight |
|---------------|----------|-----------|-------------|--------|--------|
| **172** (first) | 1h 30m | 6 | Accumulation up to 100 | 20/q | 25% |
| **371** (second) | 2h – 2h 15m | 6 | Accumulation up to 100 | 20–22/q | 35% |
| **372** (third) | 2h – 2h 30m | 6 | **Choose 4** of 6 | 25–28/q | 40% |

**371 internal structure (6 questions = 2 per cluster):**
1. **אשכול חברה ומדע** — statistics, probability, science-in-context
2. **התמצאות במישור ובמרחב** — plane/space reasoning, similarity, trig
3. **אשכול פיננסי-כלכלי** — growth/decay, percentages, financial word problems

### Key structural difference: Old 382 vs. New 372

| Topic | Old 382 (803) | New 372 |
|-------|---------------|---------|
| Analytic geometry (circles) | ✅ Core | ❌ Removed |
| Calculus (polynomials, tangents, integrals) | ✅ 2–3 questions/exam | ❌ Removed |
| Linear programming (תכנון לינארי) | ❌ | ✅ Added |
| Quadratic models (מודל ריבועי) | ❌ | ✅ Added |
| Spatial reasoning / volumes | Limited | ✅ Expanded |
| Sequences | In 381 | Redistributed |

---

## 1.2 Topic Coverage by Questionnaire (2015–2024)

### Questionnaire 182 / 172 — First Paper (~25%)

**Section model:** Open pool — 6 questions, accumulation scoring.

| Topic | Frequency (2015–24) | Sub-topics tested | Typical pts |
|-------|---------------------|-------------------|-------------|
| Graph reading (קריאת גרפים) | ~90% of exams | Distance-time, rates, comparisons, qualitative slope | 20–25 |
| Statistics | ~85% | Mean, median, mode, frequency tables, pie/bar charts | 20–25 |
| Probability | ~80% | Simple events, complements, without replacement | 20–25 |
| Word problems (קנייה/מכירה) | ~75% | Purchases, percentages, chained discounts | 20–25 |
| Area/perimeter | ~70% | Composite shapes, rectangles, triangles | 20–25 |
| Arithmetic sequences | ~50% | nth term, sum (old track); reduced in new 172 | 20–25 |

### Questionnaire 381 / 371 — Second Paper (~35%)

**Old 381 topics (2015–2024):**

| Topic | Frequency | Sub-topics | Typical pts |
|-------|-----------|------------|-------------|
| Algebra + graphs | Every year | Systems, parabola-line intersection, word problems | 25 |
| Growth/decay (גדילה ודעיכה) | ~95% | Geometric sequences, compound change | 25 |
| Probability | ~90% | Tree diagrams, conditional, two-/three-stage | 25 |
| Trigonometry (plane) | ~85% | Right triangles, sin/cos/tan applications | 25 |
| Statistics | ~80% | Mean, median, std dev, comparing datasets | 25 |
| Analytic geometry (basic) | ~60% | Midpoints, distances, line equations | 25 |

**New 371 topic frequency (Geva analysis, 18 exams 2020–2024):**

| Topic | Appearances / 18 exams | % | Notes |
|-------|------------------------|---|-------|
| Growth/decay | 19 question slots | ~95% | Nearly every exam, often 2 questions |
| Probability (tree/dependent) | 17 | ~94% | Dominant prob format |
| Similar triangles (דמיון) | 14 | ~78% | Cluster 2 staple |
| Trigonometry (plane) | 15+ | ~83% | Always with diagram |
| Percentages/financial | 12 | ~67% | Cluster 3 |
| Statistics (central tendency) | 8 | ~44% | Mean/median/mode |
| Standard deviation | 2 | ~11% | Rare but tested |
| Scale/proportion | 4 | ~22% | Map scale, similarity ratios |

### Questionnaire 382 / 372 — Third Paper (~40%)

**Old 382 (2015–2024) — Algebra + Calculus focus:**

| Topic | Frequency | Sub-topics | Typical pts |
|-------|-----------|------------|-------------|
| Calculus — investigation | ~95% | Domain, extrema, increasing/decreasing, graph matching | 25 |
| Calculus — tangent line | ~80% | Derivative, tangent equation | 25 |
| Calculus — area (integrals) | ~75% | Definite integral, area between curves | 25 |
| Word problems | ~85% | Purchase, motion, geometry context | 25 |
| Analytic geometry | ~70% | Lines, parabolas, circles, distances | 25 |
| Pure algebra systems | ~60% | 2×2 systems, parameters | 25 |

**New 372 topics:**

| Topic | Expected frequency | Sub-topics |
|-------|-------------------|------------|
| Linear programming | High (new) | Feasible region, corner-point evaluation |
| Quadratic modeling | High (new) | Vertex form, fitting, optimization |
| Spatial reasoning | High | Volume of prisms, cylinders, 3D visualization |
| Statistics (normal distribution) | Medium | Reading normal curve, probability from graph |
| Algebra word problems | Every year | No calculus required |

---

## 1.3 Question Type Analysis (3pt)

| Type | Share of items | Description |
|------|----------------|-------------|
| **Computational** | ~55% | Solve equations, calculate areas, compute probabilities |
| **Graph reading / construction** | ~25% | Interpret or sketch real-world graphs |
| **Justification ("נמק")** | ~15% | Explain why median changed, justify graph choice |
| **Formal proof** | ~5% | Rare at 3pt; mostly "explain" not full deductive proof |

**Classic archetypes (appear almost every year on old track):**
1. Distance-time graph with meeting/overtaking (182/381)
2. Purchase chain with percentage markup/discount (381/382)
3. Geometric sequence population/model (381)
4. Tree diagram without replacement (381)
5. Polynomial investigation + graph selection from 4 options (382)
6. Tangent line to √x or polynomial (382)
7. Area under polynomial using definite integral (382)

**Multi-step patterns:**
- Part (a) compute → (b) use result in new scenario → (c) compare/justify
- Parameter introduction in part (c) or (d)

---

## 1.4 Minimum Prerequisites (3pt)

- Linear and quadratic equations, systems (2×2)
- Percentages, ratio, proportion
- Basic statistics (mean, median, mode)
- Simple probability (counting outcomes)
- Right-triangle trigonometry
- Function graphs (linear, quadratic) — read, not full calculus on new track
- **Old track only:** Basic derivatives, tangent lines, definite integrals of polynomials

---

# Part 2: Four Units (4 יחידות לימוד)

## 2.1 Exam Structure

### Old Curriculum — 481 / 482

| Questionnaire | Duration | Structure | Choice rule | Points | Weight |
|---------------|----------|-----------|-------------|--------|--------|
| **481** (804) | 3h 30m – 4h 15m | 3 chapters, 8 questions | **5 of 8** (2022–23) or **4 of 8** with ≥1/chapter (2024+) | 20–25/q | 65% |
| **482** (805) | 1h 40m – 2h | 2 chapters, 5 questions | **3 of 5**, ≥1 per chapter | 33.3/q | 35% |

**481 chapter constraints (old):**

| Chapter | Topics | Choose |
|---------|--------|--------|
| **פרק א** | Algebra word problems, analytic geometry, probability | 2 of 3 |
| **פרק ב** | Euclidean geometry, plane trigonometry | 1 of 2 |
| **פרק ג** | Calculus: polynomials, rational, root functions | 2 of 3 |

**482 chapter constraints (old):**

| Chapter | Topics | Choose |
|---------|--------|--------|
| **פרק א** | Sequences, trigonometry in space | 1 of 2 |
| **פרק ב** | Growth/decay, trig/exp/log/power calculus | 2 of 3 |

### New Curriculum — 471 / 472

| Questionnaire | Duration | Structure | Choice rule | Points | Weight |
|---------------|----------|-----------|-------------|--------|--------|
| **471** | 3h 30m – 4h 15m | 3 chapters, 8 questions | **4 of 8**, ≥1 per chapter | 25/q | 65% |
| **472** | 1h 45m – 2h | 2 chapters, 5 questions | **3 of 5**, ≥1 per chapter | 33.3/q | 35% |

**471 chapters (new):**

| Chapter | Topics |
|---------|--------|
| **פרק א** | Statistics, probability, sequences |
| **פרק ב** | Geometry (integrated: plane + analytic + trig) |
| **פרק ג** | Calculus: polynomials, rational, root functions |

**472 chapters (new):**

| Chapter | Topics |
|---------|--------|
| **פרק א** | Statistics (hypothesis testing), growth/decay, sequences, vectors |
| **פרק ב** | Calculus: exponential, logarithmic, power functions |

---

## 2.2 Topic Coverage (2015–2024)

### 481 / 471 — First Paper

| Topic | Frequency | Sub-topics | Pts |
|-------|-----------|------------|-----|
| **Word problems (motion, work, mixtures)** | ~90% | Relative speed, meeting, delayed start, parameter | 20–25 |
| **Probability** | ~85% | Conditional, Bayes-style, without replacement, parameters | 20–25 |
| **Analytic geometry** | ~80% | Lines, circles, tangents, locus | 20–25 |
| **Calculus — rational functions** | ~90% | Asymptotes, investigation, area | 20–25 |
| **Calculus — polynomials** | ~85% | Extrema, inflection, sketch, parameter k | 20–25 |
| **Calculus — root functions** | ~75% | Domain, derivative, tangent | 20–25 |
| **Euclidean geometry** | ~70% | Proofs, circles, similarity, quadrilaterals | 20–25 |
| **Plane trigonometry** | ~70% | Sine/cosine laws, area formulas | 20–25 |
| **Optimization (word)** | ~60% | Single-variable max/min in context | 20–25 |

### 482 / 472 — Second Paper

| Topic | Frequency | Sub-topics | Pts |
|-------|-----------|------------|-----|
| **Growth/decay (continuous)** | ~90% | $A = A_0 e^{kt}$, half-life, parameter finding | 33 |
| **Trig function calculus** | ~85% | $f(x)=\sin x \cdot \cos x$, extrema, sketch | 33 |
| **Exp/log calculus** | ~80% | $e^{ax}$, $\ln x$, combined investigation | 33 |
| **Sequences (arith + geom)** | ~75% | Sum formulas, recursion, comparison | 33 |
| **Trig in space** | ~70% | Angles line-plane, box diagonals | 33 |
| **Vectors (new 472)** | Emerging | Dot product basics, geometric applications | 33 |

---

## 2.3 Question Type Analysis (4pt)

| Type | Share | Notes |
|------|-------|-------|
| **Multi-step computation** | ~40% | 4–7 sub-items per question |
| **Graph sketch / match** | ~20% | Select correct graph from 4 options with justification |
| **Geometric proof** | ~15% | "הוכח" — cyclic quads, similarity, tangents |
| **Parameter analysis** | ~15% | Find $a$, $k$, $t$ ranges; discuss number of solutions |
| **True/false with justification** | ~10% | "I/II — state if true, justify" |

**Classic 481 archetypes:**
1. Motion with graphs (distance-time, meeting/overtaking)
2. Basket/urn probability with conditional follow-up
3. Circle + tangent analytic geometry
4. Rational function full investigation + area
5. Geometry proof with circle / cyclic quadrilateral

**Classic 482 archetypes:**
1. Two trig functions intersection + enclosed area with parameter
2. Exponential growth vs. linear comparison
3. Geometric sequence sum / infinite series threshold
4. 3D trig — angle between diagonal and face

---

## 2.4 Minimum Prerequisites (4pt)

All 3pt topics plus:
- Full derivative rules (product, quotient, chain for compositions)
- Integration: polynomials, simple rational, $\int e^{ax}$, $\int \sin(ax)\,dx$
- Trig identities (basic: $\sin^2+\cos^2=1$, double angle used in calc)
- Sequences: arithmetic + geometric, finite and infinite sums
- Analytic geometry: circle equation, tangent to circle
- Probability: conditional, independent, tree diagrams

---

# Part 3: Five Units (5 יחידות לימוד)

## 3.1 Exam Structure

### Old Curriculum — 581 / 582

| Questionnaire | Duration | Structure | Choice rule | Points | Weight |
|---------------|----------|-----------|-------------|--------|--------|
| **581** (806) | 3h 30m – 4h 15m | 3 chapters, 8 questions | **4 of 8**, ≥1/chapter | 25/q | 60% |
| **582** (807) | 2h 15m – 2h 45m | 2 chapters, 5 questions | **3 of 5**, ≥1/chapter | 33.3/q | 40% |

**581 chapters (old):**

| Chapter | Topics | Choose |
|---------|--------|--------|
| **פרק א** | Algebra, sequences, probability | 2 of 3 |
| **פרק ב** | Geometry + plane trigonometry | 1 of 2 |
| **פרק ג** | Calculus + optimization (poly, rational, root, trig) | 2 of 3 |

**582 chapters (old):**

| Chapter | Topics | Choose |
|---------|--------|--------|
| **פרק א** | Analytic geometry, vectors, trig in space, complex numbers | 2 of 3 |
| **פרק ב** | Growth/decay, power/exp/log calculus | 1 of 2 |

### New Curriculum — 571 / 572

| Questionnaire | Duration | Structure | Choice rule | Points | Weight |
|---------------|----------|-----------|-------------|--------|--------|
| **571** | 3h 30m – 4h 15m | **4 chapters**, 8 questions | **4 of 8** (2024) or **5 of 8** (2025+); constraints on chapters | 20–25/q | 60% |
| **572** | 2h – 2h 15m | 2 chapters, 5 questions | **3 of 5** | 33.3/q | 40% |

**571 chapters (new — evolving):**

| Chapter | Topics | Choose |
|---------|--------|--------|
| **פרק א** | Short questions (4 sub-items: induction, trig, investigation, optimization) | 2–3 of 4 sub-items OR 1 full short question |
| **פרק ב** | Induction, sequences, probability | 1 of 2 |
| **פרק ג** | Geometry + plane trigonometry | 1 of 2 |
| **פרק ד** | Calculus + optimization (poly, rational, root, trig) | 2 of 3 |

**572 chapters (new):**

| Chapter | Topics | Choose |
|---------|--------|--------|
| **פרק א** | Analytic geometry, vectors, trig in space, complex numbers | 2 of 3 |
| **פרק ב** | Exp/log calculus (power functions removed) | 1 of 2 |

**Notable 571 changes vs. 581:**
- Removed: dedicated motion/power word-problem blocks
- Added: **mathematical induction** (אינדוקציה), short-question section
- 2025+: 5 questions × 20 pts instead of 4 × 25

---

## 3.2 Topic Coverage (2015–2024)

### 581 / 571 — First Paper

| Topic | Frequency | Sub-topics | Pts |
|-------|-----------|------------|-----|
| **Function investigation (full)** | Every year | Domain, asymptotes, extrema, inflection, sketch, parameter | 25 |
| **Optimization (geometry/context)** | ~95% | Cylinder/box max volume, fence problems, constraint setup | 25 |
| **Probability (advanced)** | ~90% | Binomial, conditional chains, complementary events | 25 |
| **Sequences** | ~85% | Geometric infinite, recursion, sum comparison | 25 |
| **Geometry proof (Euclidean)** | ~80% | Circles, tangents, cyclic quads, angle chasing | 25 |
| **Plane trigonometry** | ~75% | Identity application, trig equations in context | 25 |
| **Induction (new 571)** | ~60% (2024+) | Sum formulas, divisibility | 20 |
| **Short questions block (571)** | New | Mixed topics, 4 sub-items | 20–25 |

**Representative 581 calculus sub-item chain:**
(a) Domain + asymptotes → (b) Extrema classification → (c) Match graph from 4 options with parameter → (d) Area/optimization with second function $g(x)=af(x)$

### 582 / 572 — Second Paper

| Topic | Frequency | Sub-topics | Pts |
|-------|-----------|------------|-----|
| **Complex numbers** | ~85% | De Moivre, roots of unity, geometric locus in Gauss plane | 33 |
| **Vectors / analytic geometry** | ~90% | Circles, locus, perpendicular bisector, combined | 33 |
| **Trig in space** | ~75% | Angles between lines/planes, box problems | 33 |
| **Exp/log calculus** | ~90% | Full investigation, area, parameter | 33 |
| **Growth/decay** | ~80% | Continuous models, finding $k$ from conditions | 33 |
| **Hyperbola (572 new)** | ~10% (2024) | Added to curriculum; not yet frequently examined | 33 |

---

## 3.3 Question Type Analysis (5pt)

| Type | Share | Notes |
|------|-------|-------|
| **Full function investigation + sketch** | ~30% | Always multi-part, often with parameter |
| **Proof (geometry or algebra)** | ~20% | Formal deductive structure expected |
| **Parameter range analysis** | ~20% | "For which $a$ does $f$ have…" |
| **Complex numbers (compute + geometric)** | ~15% | Roots, locus, polygon area in complex plane |
| **Optimization setup + solve** | ~15% | Constraint equation → single-variable calc |

**5pt-specific demands:**
- **Second derivative** routinely required for inflection/concavity
- **Graph matching** with 3–4 parameter-dependent options
- **Area between curves** and **volume of revolution** (582)
- **Integration by substitution** for composite functions
- Induction write-ups must show base case + inductive step explicitly

---

## 3.4 Minimum Prerequisites (5pt)

All 4pt topics plus:
- Mathematical induction
- Binomial probability / Bernoulli trials
- Full trig identity set (addition formulas, double angle)
- Complex numbers: arithmetic, polar form, De Moivre, roots
- Vectors: 2D/3D, dot product, projections
- Advanced integration (substitution, some rational functions)
- Volume of solids of revolution

---

# Part 4: Difficulty Progression (3pt → 4pt → 5pt)

## 4.1 Topics Exclusive or Near-Exclusive to Higher Levels

| Topic | 3pt | 4pt | 5pt |
|-------|-----|-----|-----|
| Linear programming | New 372 only | ❌ | ❌ |
| Quadratic modeling (372) | New 372 | ❌ | ❌ |
| Basic calculus (old 382) | Old only | ✅ | ✅ |
| Rational function investigation | ❌ | ✅ | ✅ |
| Trig function calculus | ❌ | ✅ | ✅ |
| Sequences (formal) | Limited | ✅ | ✅ |
| Trig in space | ❌ | ✅ | ✅ |
| Vectors | ❌ | New 472 | ✅ |
| Complex numbers | ❌ | ❌ | ✅ |
| Mathematical induction | ❌ | ❌ | ✅ (571) |
| Binomial distribution | ❌ | ❌ | ✅ |
| Volume of revolution | ❌ | ❌ | ✅ |
| Full Euclidean proof chains | ❌ | Medium | Heavy |
| Short-question mixed section | ❌ | ❌ | ✅ (571) |

## 4.2 Same Topic, Increasing Depth

| Topic | 3pt depth | 4pt depth | 5pt depth |
|-------|-----------|-----------|-----------|
| **Probability** | Simple counting, 1–2 stage trees | Conditional, parameters, multi-stage | Binomial, Bayes, complementary with conditions |
| **Trigonometry** | Right triangle, find side/angle | Sine/cosine laws, trig equations | Identities in proofs, trig calc, 3D angles |
| **Functions** | Read graphs, linear/quadratic | Investigate rational/root | Full investigation + optimization + parameter |
| **Geometry** | Areas, basic analytic | Proofs, circles, analytic | Cyclic quads, complex-geometric locus |
| **Sequences** | Arithmetic (381/371) | Arith + geom, sums | Infinite geom, recursion, induction link |
| **Calculus** | Basic derivative/integral (old) | Area, tangent, extrema | Inflection, substitution, volumes, related rates style |

---

# Part 5: Dependency Trees

## 5.1 Core Dependencies (All Levels)

```
Percentages / ratios
  └── Word problems (purchase, markup, discount)
  └── Growth/decay (discrete → continuous)
        └── Geometric sequences
              └── Exp/log functions (4pt+)

Linear equations
  └── Systems (2×2)
        └── Analytic geometry (intersection of lines)
              └── Circle equations (4pt+)

Quadratic functions
  └── Parabola geometry
  └── Optimization (vertex) — 3pt/4pt
```

## 5.2 Probability Chain

```
Basic counting (sample space)
  └── Independent events
        └── Multiplication rule
              └── Tree diagrams (2-stage → 3-stage)
                    └── Conditional probability P(A|B)
                          └── Bayes / total probability (4pt+)
                                └── Binomial distribution (5pt)
                                      └── Depends on: combinations (nCk), sequences
```

## 5.3 Calculus Chain

```
Function concept + graph reading
  └── Limits (intuitive → formal at 5pt)
        └── Derivative (definition → rules)
              ├── Chain rule
              │     └── Trig/exp/log derivatives (4pt/5pt)
              ├── Product/quotient rules
              │     └── Rational function investigation
              └── Second derivative
                    └── Inflection, concavity (4pt/5pt)
                          └── Full sketch + optimization
                                └── Integral (antiderivative)
                                      ├── Area between curves
                                      ├── Substitution method (5pt)
                                      └── Volume of revolution (5pt)
```

## 5.4 Geometry Chain

```
Pythagorean theorem
  └── Distance formula
        └── Analytic geometry (lines, circles)
              └── Vectors (4pt new / 5pt)
                    └── Trig in space (4pt/5pt)
                          └── Complex numbers as 2D (5pt)

Similar triangles
  └── Proportion / scale
        └── Euclidean proofs (4pt/5pt)
              └── Circle theorems (5pt heavy)
```

## 5.5 Level-Specific Critical Paths

**3pt (new track) exam-ready path:**
`Percentages → Linear/quadratic systems → Graph reading → Basic statistics → Simple probability → Similar triangles → Trig (right triangle) → Linear programming / quadratic model (372)`

**4pt exam-ready path:**
`3pt foundation → Rational functions → Full derivative rules → Basic integration → Trig identities → Sequences → Analytic geometry (circle) → Conditional probability → Growth/decay continuous`

**5pt exam-ready path:**
`4pt foundation → Induction → Binomial probability → Complex numbers → Advanced integration → Volume of revolution → Formal Euclidean proofs → Parameter-heavy investigation`

---

# Part 6: Question Format & Grading Patterns

## 6.1 Sub-item Progression (Typical)

| Part | Cognitive level | Example verbs (Hebrew) |
|------|-----------------|------------------------|
| א (a) | Direct computation | מצא, חשב |
| ב (b) | Apply earlier result | השתמש, בנה |
| ג (c) | Compare / classify | קבע, הוכח, נמק |
| ד (d) | Parameter / generalization | עבור אילו ערכים, מצא $a$ |
| ה (e) | Synthesis / proof | הוכח, הסבר מדוע |

## 6.2 Graph-Related Items (~25–30% of 4pt/5pt calc questions)

- Match function to graph from 4 options with **written justification**
- Identify which horizontal line cuts graph at exactly one point
- Sketch after full investigation (marked features required)
- Read derivative graph to reconstruct original function (471 style)

## 6.3 Proof Expectations by Level

| Level | Proof type | Expected detail |
|-------|------------|-----------------|
| 3pt | Explanation | 2–4 sentences, logical connection |
| 4pt | Geometry proof | Reference theorem, chain of equal angles/sides |
| 5pt | Full deductive proof | Complete sentences, cite geometric facts, no skipped steps |

---

# Part 7: Stable vs. Variable Patterns (2015–2024 Summary)

## Stable (use for mock exam templates)

1. **Chapter structure** per questionnaire code — topic pools are fixed
2. **Choice constraints** — "at least one per chapter" on multi-chapter papers
3. **Calculator + formula sheet** policy
4. **Process grading** requirement
5. **Motion / purchase / growth** word problems at every level
6. **Multi-part escalation** within questions
7. **Parameter $a$, $k$, $t$** appearing in final sub-items
8. **Probability without replacement** at 3pt–5pt
9. **Function investigation template** at 4pt/5pt (domain → asymptotes → extrema → sketch → area)

## Variable (monitor year-to-year)

1. Points per question (Ministry adjusts for adapted exams)
2. Number of required questions (4 vs. 5 on 481/571)
3. Exam duration (extended time in 2025 for some papers)
4. New curriculum topic migration (382 calculus → 372 linear programming)
5. Specific probability format (tree vs. table vs. formula)
6. Whether induction appears as standalone or embedded

---

# Part 8: Platform Gap Analysis

Based on exam patterns vs. current platform assets (`apps/web/src/lib/mock-exams/`, `scripts/seed_data/lessons/`):

## 8.1 Mock Exam Gaps

| Gap | Priority | Recommendation |
|-----|----------|----------------|
| **No 3pt mock exam** | 🔴 High | Add `math_3pt_mock_1` mirroring 371+372 structure (new curriculum) |
| **4pt mock uses old 481 chapter layout** | 🟡 Medium | Add parallel 471-format mock (stats/probability chapter) |
| **5pt mock missing 571 short-question section** | 🔴 High | Add 4-sub-item short question block to 5pt mock |
| **No second-paper mocks (472/572/482)** | 🔴 High | 482/572 = 35–40% of grade; currently unrepresented |
| **Choice-rule metadata incomplete** | 🟡 Medium | Encode `min_per_chapter`, `max_answers`, over-answer policy in schema |
| **Duration mismatch** | 🟡 Medium | 472/572 = 105–135 min, not 210; split mock catalog by questionnaire |

## 8.2 Lesson / Curriculum Gaps

| Topic | Exam frequency | Platform status | Action |
|-------|----------------|-------------------|--------|
| **Linear programming (372)** | New, high | Likely missing | Author lesson + drill bank |
| **Quadratic modeling (372)** | New, high | Partial (`quadratic_model_fitting`) | Expand to exam-style |
| **Spatial reasoning / 3D volumes (372)** | High | Partial (`3d_solids_volume`) | Align to 3pt level (simpler) |
| **Hypothesis testing (472)** | New 4pt | Likely missing | New lesson |
| **Mathematical induction (571)** | High (5pt new) | Check coverage | Dedicated lesson if absent |
| **Short-question mixed practice (571)** | Every exam | Missing | New "exam skills" lesson type |
| **Graph matching with justification** | ~25% calc Qs | Under-taught | Add worked examples emphasizing נמק |
| **True/false + justify (I/II)** | Common 4pt geo | Rare in lessons | Add question archetype |
| **Complex numbers + geometry locus (572)** | ~85% | Has `complex_numbers_de_moivre` | Ensure polygon/locus problems |
| **Old 382 calculus (external candidates)** | Still examined | Lessons exist but may target wrong level | Tag as legacy/external track |

## 8.3 Common Student Mistakes to Address in Lessons

| Mistake | Levels | Lesson intervention |
|---------|--------|---------------------|
| Answering more questions than allowed | All | Exam-strategy section: "first N graded" rule |
| Final answer without steps | All | Require step-by-step submission format in open questions |
| Forgetting domain restrictions (roots, rational) | 4pt/5pt | Domain-first investigation template |
| Sign errors in inequality / derivative intervals | 4pt/5pt | Sign chart method |
| Confusing $P(A \cap B)$ with $P(A \mid B)$ | 3pt–5pt | Tree diagram → conditional highlight |
| Not justifying graph choice | 4pt/5pt | "Match graph" rubric with required bullet points |
| Geometry proof — skipping theorem citation | 4pt/5pt | Proof scaffold templates |
| Induction — missing base case | 5pt new | Template with explicit base + step |
| Complex roots — forgetting all $n$ roots | 5pt | De Moivre $n$-th roots checklist |
| Area sign errors (below x-axis) | 4pt/5pt | Absolute value / split interval practice |

## 8.4 Justification Level Expected

| Level | Minimum acceptable response |
|-------|----------------------------|
| 3pt | Short explanation (1–3 sentences), numeric check |
| 4pt | Structured reasoning, reference formula/theorem by name |
| 5pt | Complete deductive chain; for calc: show derivative sign table or second derivative test stated |

---

# Part 9: Mock Exam Design Specifications

Use these templates when building platform mock exams:

## 9.1 Template: 4pt Old (481)

```
Duration: 210 min | Total: 100 pts | Answer 4 of 8 (≥1 per chapter)

Chapter 1 (Algebra/Analytic/Probability): 3 questions — choose 2
Chapter 2 (Geometry/Trig plane): 2 questions — choose 1
Chapter 3 (Calculus): 3 questions — choose 2

Point split: 25 × 4 = 100
```

## 9.2 Template: 4pt New (471)

```
Duration: 255 min | Total: 100 pts | Answer 4 of 8 (≥1 per chapter)

Chapter 1 (Statistics/Probability/Sequences): 3 Q — choose ≥1
Chapter 2 (Integrated geometry): 2 Q — choose ≥1
Chapter 3 (Calculus): 3 Q — choose ≥1

Point split: 25 × 4 = 100
```

## 9.3 Template: 5pt New (571) — 2025 format

```
Duration: 255 min | Total: 100 pts | Answer 5 of 8

Chapter 1 (Short questions): 1 Q with 4 sub-items — choose 2 sub-items OR treat as 1 Q
Chapter 2 (Induction/Sequences/Probability): 2 Q — choose 1
Chapter 3 (Geometry/Trig): 2 Q — choose 1
Chapter 4 (Calculus/Optimization): 3 Q — choose 2

Point split: 20 × 5 = 100
Constraint: ≥1 from Ch1 OR Ch2 combined, ≥1 from Ch3, ≥1 from Ch4
```

## 9.4 Template: 3pt New (371)

```
Duration: 135 min | Total: 100 pts | Accumulation (6 Q × 20 pts, cap 100)

Cluster A (Society/Science): 2 Q — statistics, probability
Cluster B (Spatial): 2 Q — similarity, trig, scale
Cluster C (Financial): 2 Q — growth/decay, percentages

Student strategy: pick strongest 5 questions (100 pts) or 4×25 if adapted
```

---

# Part 10: Source Index

| Source | URL / Location | Used for |
|--------|----------------|----------|
| Ministry exam archive | `meyda.education.gov.il/sheeloney_bagrut/` | Official booklets 2018–2024 |
| New curriculum portal | `pop.education.gov.il/.../new-curriculum/` | 172–572 structure |
| BagrutOnline curriculum PDFs | `bagrutonline.co.il/uploads/file/` | Topic lists per level |
| Yoel Geva exam structure | `geva.co.il/bagrut/math/` | Weights, chapter rules |
| Geva 371 prep booklet | 18 exams 2020–2024 topic index | Frequency analysis |
| Melumad structure guide | `melumad.co.il/מבנה-הבגרות-במתמטיקה/` | Old/new mapping |
| m-math.co.il curriculum diff | New vs. old topic changes | 372/571/572 deltas |
| OpenBook 2025 schedule | `openbook.co.il/Page/points_times_2005` | 2025 durations/points |
| Wikipedia / Hamichlol | Exam structure summaries | Cross-validation |
| Platform mock exams | `apps/web/src/lib/mock-exams/` | Gap analysis |

---

# Appendix A: Questionnaire Code Quick Reference

| Level | Old code | New code | Ministry ID prefix |
|-------|----------|----------|-------------------|
| 3pt Q1 | 182 (801) | 172 | 035182 / 035172 |
| 3pt Q2 | 381 (802) | 371 | 035381 / 035371 |
| 3pt Q3 | 382 (803) | 372 | 035382 / 035372 |
| 4pt Q1 | 481 (804) | 471 | 035481 / 035471 |
| 4pt Q2 | 482 (805) | 472 | 035482 / 035472 |
| 5pt Q1 | 581 (806) | 571 | 035581 / 035571 |
| 5pt Q2 | 582 (807) | 572 | 035582 / 035572 |

---

# Appendix B: Recommended Next Steps for Curriculum Team

1. **Split mock exam catalog** by questionnaire (471 vs 481, 571 vs 581, 371/372 vs 381/382).
2. **Add 3pt mock** aligned to new curriculum clusters (172/371/372).
3. **Author "exam skills" micro-lessons**: graph matching, proof scaffolds, induction template, exam choice strategy.
4. **Tag lessons** with `curriculum_track: old | new | both` and `questionnaire: [371, 372, ...]`.
5. **Build dependency graph in KG** from Section 5 chains — wire as prereqs for path planner.
6. **Calibrate lesson difficulty** to sub-item (c)/(d) level for 4pt/5pt, not just (a)/(b).
7. **Monitor 2025–2026 Ministry circulars** for continued structure changes (571: 4 vs 5 questions).

---

*Report generated: June 30, 2026. Exam structures verified against Ministry booklets through Summer 2025 (תשפ"ה). Re-verify before high-stakes deployment.*
