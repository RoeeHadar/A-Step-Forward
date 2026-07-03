---
concept_id: "basic_probability"
name: "Basic Probability (Classical)"
name_he: "הסתברות בסיסית (קלאסית)"
subject: math
level: high_school
bagrut_chapter: probability
points_levels: ["3pt"]
expansion_status: todo
data_completeness: full
lesson_id: "probability_basic"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/probability_basic.json
prerequisites: ["fractions_algebraic", "arithmetic"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Basic Probability (Classical)

**HE:** הסתברות בסיסית (קלאסית)

## Lesson overview

**Lesson:** Probability Fundamentals — Sample Spaces, Events & Bayes' Theorem
**HE:** יסודות ההסתברות — מרחבי מדגם, מאורעות ומשפט בייס

Kolmogorov's axioms, conditional probability, independence, the law of total probability, and Bayes' theorem with the medical-test application.

> אקסיומות קולמוגורוב, הסתברות מותנית, אי-תלות, חוק ההסתברות הכוללת ומשפט בייס עם יישום בדיקה רפואית.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/fractions_algebraic|fractions_algebraic]], [[concepts/arithmetic|arithmetic]]

## Skill atoms

- Classical probability: P(A) = favorable/total
- Complementary event: P(Aᶜ) = 1-P(A)
- Union of mutually exclusive events
- Tree diagrams for two-stage experiments
- Two-way tables for joint outcomes
- Independent vs dependent events (intro)

## Level scope

- **3pt:** Bagrut 372 probability — classical formula, complement, simple trees

## Lesson sections

- **intro:** Quantifying Uncertainty
- **definition:** Sample Space, Events, and Probability Axioms
- **theory:** Key Theorems
- **worked_example:** Worked Example 1 — Drawing an Ace from a Deck
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Computing Conditional Probability
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Medical Test (Bayes' Theorem)
- **method_guide:** Method Guide — Probability Toolkit
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/probability_conditional_bayes|probability_conditional_bayes]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/probability_basic.json` _(alias from `basic_probability`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
