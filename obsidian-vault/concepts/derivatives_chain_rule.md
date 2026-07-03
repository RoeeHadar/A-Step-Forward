---
concept_id: "derivatives_chain_rule"
name: "Derivatives — Chain Rule"
name_he: "נגזרות — כלל השרשרת"
subject: math
level: high_school
bagrut_chapter: calculus
points_levels: ["4pt", "5pt"]
expansion_status: todo
data_completeness: full
lesson_id: "derivatives_rules"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/derivatives_rules.json
prerequisites: ["derivatives_polynomial_rational"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Derivatives — Chain Rule

**HE:** נגזרות — כלל השרשרת

## Lesson overview

**Lesson:** Differentiation Rules
**HE:** כללי גזירה

Four core differentiation rules — sum/difference, product, quotient, and chain rule — allow us to differentiate virtually any elementary function without returning to the limit definition.

> ארבעה כללי גזירה מרכזיים — סכום/הפרש, מכפלה, מנה ושרשרת — מאפשרים לגזור כמעט כל פונקציה אלמנטרית ללא חזרה להגדרת הגבול.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/derivatives_polynomial_rational|derivatives_polynomial_rational]]

## Skill atoms

- Chain rule: (f(g(x)))′ = f′(g(x))·g′(x)
- Identifying inner and outer functions
- Chain rule on cos(ax+b), sin(x²), (x²+1)ⁿ
- Chain rule on e^f(x) and ln(f(x))
- Combining chain with product/quotient rules
- Second derivative via repeated differentiation

## Level scope

- **4pt:** 472 — chain rule on standard composite forms
- **5pt:** 581 — nested compositions in full investigation

## Lesson sections

- **intro:** Why Rules Instead of the Definition?
- **definition:** The Four Rules
- **theory:** How the Rules Work Together
- **worked_example:** Worked Example 1 — Power and Sum Rule
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Product Rule on $x^2 e^x$
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Chain Rule + Quotient Rule
- **method_guide:** Method Guide — Which Rule Applies When
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/derivatives_polynomial_rational|derivatives_polynomial_rational]]
- [[concepts/derivatives_trigonometric|derivatives_trigonometric]]
- [[concepts/derivatives_exponential_logarithm|derivatives_exponential_logarithm]]
- [[concepts/derivatives_implicit|derivatives_implicit]]
- [[concepts/partial_derivatives|partial_derivatives]]
- [[concepts/gradient_directional_derivative|gradient_directional_derivative]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/derivatives_rules.json` _(alias from `derivatives_chain_rule`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
