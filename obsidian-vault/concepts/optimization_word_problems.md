---
concept_id: "optimization_word_problems"
name: "Optimization Word Problems"
name_he: "בעיות קיצון מילוליות"
subject: math
level: high_school
bagrut_chapter: calculus
points_levels: ["4pt", "5pt"]
expansion_status: todo
data_completeness: full
lesson_id: "optimization_problems"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/optimization_problems.json
prerequisites: ["function_analysis_extrema", "geometry_basics"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Optimization Word Problems

**HE:** בעיות קיצון מילוליות

## Lesson overview

**Lesson:** Optimization — Finding Extrema
**HE:** אופטימיזציה — מציאת קיצונים

Optimization uses calculus to find where a function achieves its maximum or minimum. The first derivative test identifies critical points; the second derivative test determines whether they are maxima or minima. Applied problems require setting up the objective function first.

> אופטימיזציה משתמשת בחשבון דיפרנציאלי למציאת מקסימום או מינימום פונקציה. מבחן הנגזרת הראשונה מזהה נקודות קריטיות; מבחן הנגזרת השנייה קובע אם הן מקסימום או מינימום. בבעיות שימושיות יש להגדיר קודם את פונקציית המטרה.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/function_analysis_extrema|function_analysis_extrema]], [[concepts/geometry_basics|geometry_basics]]

## Skill atoms

- Translating word problem to objective function
- Constraint equation from geometry context
- Expressing single variable to optimize
- Finding critical point and verifying max/min
- Domain restrictions from physical context
- Area/perimeter optimization in plane geometry
- Interpreting answer with units

## Level scope

- **4pt:** 472 applied max/min — area, perimeter, simple 3D volume setup
- **5pt:** 581 guaranteed question — multi-step geometric constraint

## Lesson sections

- **intro:** Optimization Everywhere
- **definition:** Critical Points and the Two Derivative Tests
- **theory:** Solving Applied Optimization
- **worked_example:** Worked Example 1 — Find Max/Min of $f(x)=x^2-4x+3$ on $[0,5]$
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Rectangle of Maximum Area with Fixed Perimeter
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Farmer's Fence Problem
- **method_guide:** Method Guide — First vs. Second Derivative Test
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/optimization_problems.json` _(alias from `optimization_word_problems`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
