---
concept_id: "uni_integrals"
name: "Integrals"
name_he: "אינטגרלים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "integrals_intro"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/integrals_intro.json
prerequisites: ["uni_derivatives"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Integrals

**HE:** אינטגרלים

## Lesson overview

**Lesson:** Introduction to Integration
**HE:** מבוא לאינטגרציה

Antiderivatives, indefinite integrals, and basic integration rules. The connection between differentiation and integration (FTC). Power rule, constant rule, basic trig and exponential integrals.

> נגזרות הפוכות, אינטגרלים לא מסויימים, וכללי אינטגרציה בסיסיים. הקשר בין גזירה ואינטגרציה (משפט יסודי החשבון). כלל החזקה, פונקציות טריגו ומעריכי.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_derivatives|uni_derivatives]]

## Skill atoms

- Antiderivative: F'(x)=f(x)
- Indefinite integral notation ∫f(x)dx=F(x)+C (mandatory +C)
- Power rule integration ∫xⁿ dx (n≠−1)
- ∫(1/x)dx=ln|x|+C (exception to power rule)
- Immediate integrals: sin, cos, eˣ, sec²x
- Linearity of integration (term-by-term, constant factor)
- FTC Part 2: ∫ₐᵇ f(x)dx=F(b)−F(a)
- Verify antiderivative by differentiation
- Initial value problem: recover f from f' and one point
- Distinguish indefinite (function +C) vs definite (number) integrals

## Level scope

- **calc1:** Antiderivatives and FTC bridge differentiation to area; omitting +C on indefinite integrals is a common exam deduction.

## Lesson sections

- **intro:** The Reverse of Differentiation
- **definition:** Antiderivative and Indefinite Integral
- **theory:** Basic Integration Rules
- **worked_example:** Worked Example 1 — Basic Antiderivatives
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Definite Integral (FTC)
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Initial Value Problem (Exam Level)
- **method_guide:** Method Guide — Integration
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away


## Links

- Lesson JSON: `scripts/seed_data/lessons/integrals_intro.json` _(alias from `uni_integrals`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
