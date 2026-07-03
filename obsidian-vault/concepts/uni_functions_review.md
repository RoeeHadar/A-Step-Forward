---
concept_id: "uni_functions_review"
name: "Functions & Pre-Calculus Review"
name_he: "פונקציות וחזרה על פרה-חשבון"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "function_basics_uni"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/function_basics_uni.json
prerequisites: []
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Functions & Pre-Calculus Review

**HE:** פונקציות וחזרה על פרה-חשבון

## Lesson overview

**Lesson:** Functions — Domain, Injectivity, Surjectivity and Bijection
**HE:** פונקציות — תחום, חד-חד ערכיות, על ועל ביחד

A function maps each input to exactly one output. Injectivity, surjectivity and bijectivity are the foundation of set theory, calculus and real analysis.

> פונקציה ממפה כל קלט לפלט יחיד. חד-חד ערכיות, על-ביות ו-ביעיה הם הבסיס לתורת הקבוצות, חשבון ואנליזה ממשית.

_14 sections · 8 questions in authored JSON._


## Prerequisites

—

## Skill atoms

- Function definition: domain, codomain, exactly-one output rule
- Distinguish function vs relation (duplicate inputs / vertical-line test)
- Injective test: f(a₁)=f(a₂) ⇒ a₁=a₂ (direct proof)
- Non-injectivity counterexample: a₁≠a₂ with equal outputs
- Surjective test: solve f(a)=b for arbitrary b in codomain
- Bijection criterion: both injective and surjective
- Range vs codomain: surjective iff range equals codomain
- Inverse function exists iff bijective; construct f⁻¹
- Horizontal line test for injectivity on ℝ→ℝ graphs
- Composition rules: injectivity/surjectivity of g∘f

## Level scope

- **calc1:** Set-theoretic functions in week 1 of Israeli calc-1; short proofs of injectivity/surjectivity and explicit inverse construction before limits.

## Lesson sections

- **intro:** What is a function?
- **definition:** Injection, surjection, bijection
- **theory:** Testing injectivity and surjectivity
- **worked_example:** Worked Example 1 — is $f(x)=x^2$ injective on $\mathbb{R}$? On $[0,\infty)$?
- **checkpoint:** Check
- **worked_example:** Worked Example 2 — prove $f(x)=2x+1$ is bijective $\mathbb{R}\to\mathbb{R}$
- **checkpoint:** Check
- **worked_example:** Worked Example 3 — bijection between $\mathbb{N}$ and $\mathbb{Z}$
- **method_guide:** Method guide
- **exercise_set:** Practice Exercises
- **pitfall:** Common pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/function_basics_uni.json` _(alias from `uni_functions_review`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
