---
concept_id: "function_transformations"
name: "Function Transformations"
name_he: "הזזות ומתיחות של פונקציות"
subject: math
level: high_school
bagrut_chapter: functions
points_levels: ["5pt"]
expansion_status: done
data_completeness: full
lesson_id: "function_transformations"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/function_transformations.json
prerequisites: ["functions_intro", "functions_quadratic"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Function Transformations

**HE:** הזזות ומתיחות של פונקציות

## Lesson overview

**Lesson:** Transformations of Functions — Shifts, Reflections, Scaling, Compositions
**HE:** טרנספורמציות של פונקציות — הזזות, שיקופים, גרימות, הרכבות

Transformations systematically modify a base function $f(x)$ to produce $g(x)=af(bx+c)+d$. Understanding each parameter's geometric effect allows sketching complex functions from simple ones. At 5pt, questions test: compositions of multiple transformations, identifying transformations from an equation or graph, and proofs about symmetry (odd/even) under transformations.

> טרנספורמציות משנות פונקציית בסיס $f(x)$ לפונקציה $g(x)=af(bx+c)+d$. ברמת 5 יח׳: הרכבות של טרנספורמציות מרובות, זיהוי טרנספורמציות ממשוואה/גרף, והוכחות על סימטריה (פונקציות אי-זוגיות/זוגיות) תחת טרנספורמציות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/functions_intro|functions_intro]], [[concepts/functions_quadratic|functions_quadratic]]

## Skill atoms

- Vertical shift: y = f(x) + k
- Horizontal shift: y = f(x-h)
- Vertical stretch/compress: y = a·f(x)
- Horizontal stretch/compress: y = f(bx)
- Reflection over x-axis: y = -f(x)
- Reflection over y-axis: y = f(-x)
- Absolute value of function: y = |f(x)|
- Combining multiple transformations

## Level scope

- **5pt:** Key tool for function analysis and graphing in exam questions

## Lesson sections

- **intro:** Why Transformations Appear at 5pt
- **definition:** The Standard Transformations
- **theory:** Order of Transformations and Symmetry
- **worked_example:** Worked Example 1 — Sketch $y = -(x-2)^2 + 3$ from $y = x^2$
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Sketch $g(x) = 2f(-x+1) - 3$ where $f(x) = e^x$
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Conditions for $g(x) = f(x-a)+b$ to Be Odd
- **method_guide:** Decision Table — Identifying and Applying Transformations
- **exercise_set:** Practice Exercises
- **pitfall:** Top Mistakes
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — 5pt Focus
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/function_transformations.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
