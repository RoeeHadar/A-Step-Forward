---
concept_id: "derivatives_rules"
name: "Derivative Rules (Chain, Product, Quotient)"
name_he: "כללי גזירה (שרשרת, מכפלה, מנה)"
subject: math
level: high_school
bagrut_chapter: calculus
points_levels: ["5pt"]
expansion_status: done
data_completeness: full
lesson_id: "derivatives_rules"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/derivatives_rules.json
prerequisites: ["derivatives_intro", "functions_exponential", "trigonometry_identities"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Derivative Rules (Chain, Product, Quotient)

**HE:** כללי גזירה (שרשרת, מכפלה, מנה)

## Lesson overview

**Lesson:** Differentiation Rules
**HE:** כללי גזירה

Four core differentiation rules — sum/difference, product, quotient, and chain rule — allow us to differentiate virtually any elementary function without returning to the limit definition.

> ארבעה כללי גזירה מרכזיים — סכום/הפרש, מכפלה, מנה ושרשרת — מאפשרים לגזור כמעט כל פונקציה אלמנטרית ללא חזרה להגדרת הגבול.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/derivatives_intro|derivatives_intro]], [[concepts/functions_exponential|functions_exponential]], [[concepts/trigonometry_identities|trigonometry_identities]]

## Skill atoms

- Product rule: (fg)' = f'g + fg'
- Quotient rule: (f/g)' = (f'g-fg')/g²
- Chain rule: (f(g(x)))' = f'(g(x))·g'(x)
- Derivatives of trigonometric functions: (sinx)'=cosx, (cosx)'=-sinx
- Derivative of eˣ and e^f(x)
- Derivative of ln(x) and ln(f(x))
- Derivative of aˣ and power functions
- Higher-order derivatives (second derivative)

## Level scope

- **5pt:** Core 5pt calculus; all differentiation rules tested in Bagrut

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

- [[concepts/derivatives_chain_rule|derivatives_chain_rule]]
- [[concepts/derivatives_polynomial_rational|derivatives_polynomial_rational]]
- [[concepts/derivatives_trigonometric|derivatives_trigonometric]]
- [[concepts/derivatives_exponential_logarithm|derivatives_exponential_logarithm]]
- [[concepts/derivatives_implicit|derivatives_implicit]]
- [[concepts/partial_derivatives|partial_derivatives]]
- [[concepts/gradient_directional_derivative|gradient_directional_derivative]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/derivatives_rules.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
