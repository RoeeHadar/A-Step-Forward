---
concept_id: "uni_line_integrals"
name: "Line & Surface Integrals"
name_he: "אינטגרלי קו ומשטח"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calculus_2"]
expansion_status: todo
data_completeness: full
lesson_id: "double_integrals"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/double_integrals.json
prerequisites: ["uni_vector_fields", "uni_multiple_integrals"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Line & Surface Integrals

**HE:** אינטגרלי קו ומשטח

## Lesson overview

**Lesson:** Double Integrals
**HE:** אינטגרלים כפולים

Double integrals over rectangles and general regions: iterated integrals, Fubini's theorem, changing order of integration, polar coordinates.

> אינטגרלים כפולים על מלבנים ואזורים כלליים: אינטגרלים מאוחדים, משפט פוביני, החלפת סדר אינטגרציה, קואורדינטות קוטביות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_vector_fields|uni_vector_fields]], [[concepts/uni_multiple_integrals|uni_multiple_integrals]]

## Skill atoms

- Line integral ∫_C f ds (scalar) vs ∫_C F·dr (vector)
- Parameterize curves for line integrals
- Work W=∫ F·dr interpretation
- Fundamental theorem for line integrals when F=∇φ
- Green's theorem ∮ P dx+Q dy = ∬(∂Q/∂x−∂P/∂y) dA
- Orientation of closed curves (CCW positive)
- Use Green's theorem to evaluate circulation or area

## Level scope

- **calculus_2:** Line integrals and Green's theorem; parameterization discipline and orientation signs are common exam traps.

## Lesson sections

- **intro:** From Single to Double Integrals
- **definition:** Iterated Integrals and Fubini's Theorem
- **theory:** When to Use Which Method
- **worked_example:** Worked Example 1 — Double Integral over a Rectangle
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Changing the Order of Integration
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Double Integral in Polar Coordinates
- **method_guide:** Method Guide — Double Integral Strategy
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/uni_multiple_integrals|uni_multiple_integrals]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/double_integrals.json` _(alias from `uni_line_integrals`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
