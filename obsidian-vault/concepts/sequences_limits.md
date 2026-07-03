---
concept_id: "sequences_limits"
name: "Sequences & Limits of Sequences"
name_he: "סדרות וגבולות סדרות"
subject: math
level: high_school
bagrut_chapter: algebra
points_levels: ["4pt", "5pt"]
expansion_status: todo
data_completeness: full
lesson_id: "sequences_arithmetic"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/sequences_arithmetic.json
prerequisites: ["sequences_arithmetic", "sequences_geometric"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Sequences & Limits of Sequences

**HE:** סדרות וגבולות סדרות

## Lesson overview

**Lesson:** Arithmetic Sequences — Formula and Sum
**HE:** סדרות חשבוניות — נוסחה וסכום

In an arithmetic sequence each term increases by a fixed common difference d. The nth term is a_n = a_1 + (n−1)d and the sum of n terms is S_n = n(a_1 + a_n)/2.

> בסדרה חשבונית כל איבר גדל ב-d קבוע. האיבר ה-n הוא a_n = a_1 + (n−1)d וסכום n איברים הוא S_n = n(a_1 + a_n)/2.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/sequences_arithmetic|sequences_arithmetic]], [[concepts/sequences_geometric|sequences_geometric]]

## Skill atoms

- Arithmetic sequence nth term and sum
- Geometric sequence nth term and sum
- Infinite geometric series when |q|<1
- lim aₙ as n→∞ for geometric sequences
- Connecting sequence limit to function limit
- Growth/decay word problems as geometric
- Mathematical induction on sequence formulas (5pt)

## Level scope

- **4pt:** 472 — arithmetic + geometric; finite and infinite sums
- **5pt:** 581 — sequence limits bridge to calculus; induction proofs

## Lesson sections

- **intro:** What Is an Arithmetic Sequence?
- **definition:** Arithmetic Sequence — Key Formulas
- **theory:** Why Does the Sum Formula Work?
- **worked_example:** Worked Example 1 — Finding a₁₀ and S₁₀
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Finding a₁ and d from Two Terms
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Finding n for a Given Sum
- **method_guide:** Method Guide — Arithmetic Sequences
- **exercise_set:** Practice Exercises
- **pitfall:** Top 3 Mistakes to Avoid
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Card
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/mathematical_induction|mathematical_induction]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/sequences_arithmetic.json` _(alias from `sequences_limits`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
