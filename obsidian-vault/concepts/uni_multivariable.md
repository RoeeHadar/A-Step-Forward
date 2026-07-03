---
concept_id: "uni_multivariable"
name: "Multivariable Calculus"
name_he: "חשבון רב-משתני"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calculus_2"]
expansion_status: todo
data_completeness: full
lesson_id: "multivariable_limits"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/multivariable_limits.json
prerequisites: ["uni_derivatives", "uni_integrals"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Multivariable Calculus

**HE:** חשבון רב-משתני

## Lesson overview

**Lesson:** Limits of Multivariable Functions
**HE:** גבולות של פונקציות ממשתנים רבים

Limits in two or more variables: path-dependence, showing limits DNE, polar coordinates approach.

> גבולות בשני משתנים ויותר: תלות בנתיב, הראת שגבול לא קיים, גישת קואורדינטות קוטביות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_derivatives|uni_derivatives]], [[concepts/uni_integrals|uni_integrals]]

## Skill atoms

- Functions z=f(x,y) and level curves f(x,y)=c
- Multivariable limit along different paths (path dependence)
- Continuity at a point in ℝ²
- Partial derivatives ∂f/∂x and ∂f/∂y as single-variable limits
- Mixed partials and Clairaut's theorem conditions
- Gradient vector ∇f and direction of steepest ascent
- Tangent plane to z=f(x,y) at (a,b)
- Chain rule for multivariable compositions

## Level scope

- **calculus_2:** Opening calc-2 multivariable chapter; limits, partials, gradient, and tangent-plane setup before integration in higher dimensions.

## Lesson sections

- **intro:** Why Multivariable Limits Are Harder
- **definition:** Definition of the Multivariable Limit
- **theory:** Three Strategies
- **worked_example:** Worked Example 1 — Limit DNE via Path Test
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Limit Exists via Squeeze Theorem
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Polar Coordinates Analysis
- **method_guide:** Method Guide — Strategy Selection
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/multivariable_limits.json` _(alias from `uni_multivariable`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
