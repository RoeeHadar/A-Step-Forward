---
concept_id: "uni_vector_fields"
name: "Vector Fields"
name_he: "שדות וקטוריים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calculus_2"]
expansion_status: todo
data_completeness: full
lesson_id: "partial_derivatives"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/partial_derivatives.json
prerequisites: ["uni_multivariable"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Vector Fields

**HE:** שדות וקטוריים

## Lesson overview

**Lesson:** Partial Derivatives
**HE:** נגזרות חלקיות

Partial derivatives: definition, computation, geometric meaning, mixed partials, Clairaut's theorem, and the gradient vector.

> נגזרות חלקיות: הגדרה, חישוב, משמעות גיאומטרית, נגזרות מעורבות, משפט קלרו, ווקטור הגרדיאנט.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_multivariable|uni_multivariable]]

## Skill atoms

- Vector field F(x,y)=⟨P,Q⟩ visualization
- Conservative field test: ∂P/∂y=∂Q/∂x on simply connected domain
- Potential function φ with ∇φ=F
- Divergence div F = ∂P/∂x+∂Q/∂y
- Curl in 2D as scalar ∂Q/∂x−∂P/∂y
- Flow interpretation of line integrals
- Circulation and flux over closed curves

## Level scope

- **calculus_2:** Vector fields, conservative tests, and div/curl vocabulary before line integrals and Green's theorem.

## Lesson sections

- **intro:** Rates of Change in Multiple Directions
- **definition:** Partial Derivatives — Formal Definitions
- **theory:** Geometric Meaning and Notation
- **worked_example:** Worked Example 1 — Computing Partial Derivatives
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Second-Order Partials and Clairaut's Theorem
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Gradient and Level Curves
- **method_guide:** Method Guide — Partial Derivatives Checklist
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/uni_partial_derivatives|uni_partial_derivatives]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/partial_derivatives.json` _(alias from `uni_vector_fields`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
