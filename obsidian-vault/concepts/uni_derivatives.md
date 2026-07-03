---
concept_id: "uni_derivatives"
name: "Derivatives"
name_he: "נגזרות"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "derivatives_intro"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/derivatives_intro.json
prerequisites: ["uni_limits"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Derivatives

**HE:** נגזרות

## Lesson overview

**Lesson:** Derivatives — Introduction
**HE:** נגזרות — מבוא

The derivative $f'(x)$ is the instantaneous rate of change of $f$ at $x$, formally defined as a limit. Geometrically it is the slope of the tangent line. Mastering the limit definition is the foundation of all of differential calculus.

> הנגזרת $f'(x)$ היא קצב השינוי הרגעי של $f$ ב-$x$, מוגדרת פורמלית כגבול. גיאומטרית: שיפוע המשיק. שליטה בהגדרת הגבול היא הבסיס לכל החשבון הדיפרנציאלי.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_limits|uni_limits]]

## Skill atoms

- Limit definition f'(a)=lim(f(a+h)−f(a))/h
- Difference quotient as secant slope approaching tangent
- Geometric meaning: derivative as tangent line slope
- Tangent line equation y=f(a)+f'(a)(x−a)
- Differentiability implies continuity (proof sketch)
- Non-differentiability: corners, cusps, vertical tangents, discontinuities
- Derivative as instantaneous rate of change
- Sign of f' and increasing/decreasing intervals
- Compute derivative from definition (polynomial, √x, sin x)
- Estimate derivative from graph of f

## Level scope

- **calc1:** Definition-first derivatives before rule shortcuts; calc-1 exams often require limit-definition computation for one standard function.

## Lesson sections

- **intro:** Why Derivatives?
- **definition:** The Limit Definition of the Derivative
- **theory:** Key Properties and Intuition
- **worked_example:** Worked Example 1 — Derivative of $x^2$ from Definition
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Derivative of $\sqrt{x}$ from Definition
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Derivative of $\sin x$ from Definition
- **method_guide:** Method Guide — Definition vs. Rules
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/derivatives_intro.json` _(alias from `uni_derivatives`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
