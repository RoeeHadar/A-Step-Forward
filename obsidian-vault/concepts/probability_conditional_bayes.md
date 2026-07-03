---
concept_id: "probability_conditional_bayes"
name: "Conditional Probability & Bayes"
name_he: "הסתברות מותנית ובייס"
subject: math
level: high_school
bagrut_chapter: probability
points_levels: ["4pt", "5pt"]
expansion_status: todo
data_completeness: full
lesson_id: "probability_basic"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/probability_basic.json
prerequisites: ["probability_basic"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Conditional Probability & Bayes

**HE:** הסתברות מותנית ובייס

## Lesson overview

**Lesson:** Probability Fundamentals — Sample Spaces, Events & Bayes' Theorem
**HE:** יסודות ההסתברות — מרחבי מדגם, מאורעות ומשפט בייס

Kolmogorov's axioms, conditional probability, independence, the law of total probability, and Bayes' theorem with the medical-test application.

> אקסיומות קולמוגורוב, הסתברות מותנית, אי-תלות, חוק ההסתברות הכוללת ומשפט בייס עם יישום בדיקה רפואית.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/probability_basic|probability_basic]]

## Skill atoms

- Conditional probability: P(A|B) = P(A∩B)/P(B)
- Testing independence: P(A∩B) = P(A)P(B)
- Law of total probability
- Bayes theorem: P(B|A) from P(A|B)
- Tree diagrams for multi-stage conditional
- Two-way tables with conditional rows
- Medical-test / base-rate problems

## Level scope

- **4pt:** 472 — conditional probability and two-way tables
- **5pt:** 581 — Bayes, total probability, and combinatorics link

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

- [[concepts/basic_probability|basic_probability]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/probability_basic.json` _(alias from `probability_conditional_bayes`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
