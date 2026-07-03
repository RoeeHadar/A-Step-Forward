---
concept_id: "la_vector_spaces"
name: "Vector Spaces"
name_he: "מרחבי וקטורים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_vector_spaces"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_vector_spaces.json
prerequisites: ["la_matrices", "la_vectors"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Vector Spaces

**HE:** מרחבי וקטורים

## Lesson overview

**Lesson:** Vector Spaces and Subspaces — Axioms, Span & Linear Independence
**HE:** מרחבים וקטוריים ותת-מרחבים — אקסיומות, פרישה ובלתי-תלות לינארית

Axiomatic definition of a vector space, examples and counterexamples, the three-condition subspace criterion, span as a subspace, and testing linear independence via row reduction.

> הגדרה אקסיומטית של מרחב וקטורי, דוגמאות ודוגמאות-נגד, קריטריון תת-המרחב בשלושה תנאים, קבוצת הפרישה כתת-מרחב, ובדיקת בלתי-תלות לינארית דרך דירוג שורות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/la_matrices|la_matrices]], [[concepts/la_vectors|la_vectors]]

## Skill atoms

- Vector space axioms (closure under + and scalar multiplication)
- Subspace three-condition test: 0∈W, closed under +, closed under scalar mult
- One-step subspace test: au+bv∈W for all u,v∈W
- Homogeneous linear constraint defines subspace; affine (RHS≠0) fails at 0
- span{v₁,…,vₖ} is always a subspace
- Linear independence: Σcᵢvᵢ=0 ⇒ all cᵢ=0
- Linear dependence via row reduction (rank < number of vectors)
- Matrix with vectors as columns; independent iff rank=k
- Intersection of subspaces is a subspace (template proof)
- Union W₁∪W₂ generally not a subspace unless one contains the other

## Level scope

- **la:** Abstract vector spaces and subspace proofs; row-reduction rank tests for independence are the standard computational hook on exams.

## Lesson sections

- **intro:** From Arrows to Abstract Spaces
- **definition:** Vector Space and Subspace
- **theory:** Key Theorems
- **worked_example:** Worked Example 1 — Is $W$ a Subspace of $\mathbb{R}^3$?
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Testing Linear Independence
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Prove the Intersection of Two Subspaces is a Subspace
- **method_guide:** Method Guide — Subspace & Independence Toolkit
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/vector_spaces_basis_dimension|vector_spaces_basis_dimension]]
- [[concepts/linear_transformations_kernel_image|linear_transformations_kernel_image]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/la_vector_spaces.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
