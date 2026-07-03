---
concept_id: "definite_integrals"
name: "Definite Integrals & Area"
name_he: "אינטגרל מסוים וחישובי שטחים"
subject: math
level: high_school
bagrut_chapter: integrals
points_levels: ["5pt"]
expansion_status: done
data_completeness: full
lesson_id: "definite_integrals"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/definite_integrals.json
prerequisites: ["integrals_intro"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Definite Integrals & Area

**HE:** אינטגרל מסוים וחישובי שטחים

## Lesson overview

**Lesson:** Definite Integrals and the Fundamental Theorem of Calculus
**HE:** אינטגרלים מסוימים והמשפט היסודי של החשבון

A definite integral $\int_a^b f(x)\,dx$ is a NUMBER (signed area). FTC: $\int_a^b f = F(b)-F(a)$ for any antiderivative $F$.

> אינטגרל מסוים $\int_a^b f(x)\,dx$ הוא **מספר** (שטח מסומן). FTC: $\int_a^b f = F(b)-F(a)$ לכל קדומה $F$.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/integrals_intro|integrals_intro]]

## Skill atoms

- Definite integral definition and notation
- Fundamental theorem of calculus
- Properties: linearity, additive intervals, sign
- Area under curve (above x-axis)
- Area below x-axis (taking absolute value)
- Area between two functions
- Area when functions cross (split at intersection)
- Area with parameters
- Area given derivative function
- Area between trig functions and x-axis

## Level scope

- **5pt:** Major Bagrut topic; area calculations guaranteed in every exam

## Lesson sections

- **intro:** Area as a limit of rectangles
- **definition:** Key Definitions
- **theory:** FTC and Substitution in Definite Integrals
- **worked_example:** Worked Example 1 — Basic Definite Integral
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Definite Integral with Substitution
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — FTC Part 1 and Area (Exam Level)
- **method_guide:** Method Guide — Definite Integrals
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/riemann_integral_ftc|riemann_integral_ftc]]
- [[concepts/improper_integrals|improper_integrals]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/definite_integrals.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
