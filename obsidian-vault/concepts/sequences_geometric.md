---
concept_id: "sequences_geometric"
name: "Geometric Sequences & Series"
name_he: "סדרות הנדסיות"
subject: math
level: high_school
bagrut_chapter: sequences
points_levels: ["4pt", "5pt"]
expansion_status: done
data_completeness: full
lesson_id: "sequences_geometric"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/sequences_geometric.json
prerequisites: ["exponents", "sequences_arithmetic"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Geometric Sequences & Series

**HE:** סדרות הנדסיות

## Lesson overview

**Lesson:** Geometric Sequences — Formula, Sum, and Infinite Series
**HE:** סדרות הנדסיות — נוסחה, סכום וטור אינסופי

In a geometric sequence each term is multiplied by a fixed ratio q. The nth term is a_n = a_1·q^(n−1). The finite sum is S_n = a_1(1−q^n)/(1−q). If |q|<1, the infinite sum is S_∞ = a_1/(1−q).

> בסדרה הנדסית כל איבר מוכפל במנה q קבועה. האיבר ה-n הוא a_n = a_1·q^(n−1). הסכום הסופי הוא S_n = a_1(1−q^n)/(1−q). אם |q|<1, הסכום האינסופי הוא S_∞ = a_1/(1−q).

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/exponents|exponents]], [[concepts/sequences_arithmetic|sequences_arithmetic]]

## Skill atoms

- Definition and common ratio (q)
- General term formula: aₙ = a₁·qⁿ⁻¹
- Sum formula: Sₙ = a₁(1-qⁿ)/(1-q)
- Infinite geometric series: S∞ = a₁/(1-q) when |q|<1
- Recursive definition
- Finding q from two conditions
- Mixed problems (arithmetic and geometric)
- Growth/decay as geometric sequence

## Level scope

- **4pt:** Full coverage; infinite series; growth problems
- **5pt:** Connects to limits and calculus concepts

## Lesson sections

- **intro:** Multiplicative Growth — The Power of Geometric Sequences
- **definition:** Geometric Sequence — Key Formulas
- **theory:** When Does the Infinite Sum Converge?
- **worked_example:** Worked Example 1 — Finding the 5th Term
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Infinite Sum
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Bank Account with Annual Deposits
- **method_guide:** Method Guide — Geometric Sequences
- **exercise_set:** Practice Exercises
- **pitfall:** Top 3 Mistakes to Avoid
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Card
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/series_convergence_tests|series_convergence_tests]]
- [[concepts/power_series_radius|power_series_radius]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/sequences_geometric.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
