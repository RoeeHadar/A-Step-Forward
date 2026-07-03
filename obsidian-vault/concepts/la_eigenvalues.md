---
concept_id: "la_eigenvalues"
name: "Eigenvalues & Eigenvectors"
name_he: "ערכים ווקטורים עצמיים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_eigenvalues"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_eigenvalues.json
prerequisites: ["la_determinants", "la_vector_spaces"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Eigenvalues & Eigenvectors

**HE:** ערכים ווקטורים עצמיים

## Lesson overview

**Lesson:** Eigenvalues and Eigenvectors
**HE:** ערכים עצמיים ווקטורים עצמיים

Eigenvalue equation, characteristic polynomial, finding eigenspaces, geometric vs algebraic multiplicity, and the linear independence of eigenvectors for distinct eigenvalues.

> משוואת הערך העצמי, הפולינום האופייני, מציאת מרחבים עצמיים, ריבוי גיאומטרי ואלגברי, ובלתי-תלות לינארית של וקטורים עצמיים לערכים עצמיים שונים.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/la_determinants|la_determinants]], [[concepts/la_vector_spaces|la_vector_spaces]]

## Skill atoms

- Eigenvalue equation Av=λv
- Characteristic polynomial det(A−λI)=0
- Eigenvalues of diagonal/triangular matrix from diagonal entries
- Eigenspace E_λ=ker(A−λI) via row reduction
- Verify eigenvector: check Av=λv
- trace(A)=sum of eigenvalues; det(A)=product of eigenvalues
- Algebraic vs geometric multiplicity
- Eigenvectors for distinct eigenvalues are linearly independent
- Zero eigenvalue iff A is singular (det A=0)
- Construct matrix with prescribed eigenvalues (diagonal example)

## Level scope

- **la:** Characteristic polynomial and eigenspace computation; trace/det shortcuts and multiplicity language feed directly into diagonalization.

## Lesson sections

- **intro:** Why Eigenvalues?
- **definition:** Eigenvalues, Eigenvectors, and Eigenspaces
- **theory:** Key Theorems
- **worked_example:** Worked Example 1 — Eigenvalues of an Upper Triangular Matrix
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Eigenvalues and Eigenvectors of a Symmetric Matrix
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Proof: Eigenvectors for Distinct Eigenvalues are Linearly Independent
- **method_guide:** Method Guide — Eigenvalue Computation
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/eigenvalues_eigenvectors|eigenvalues_eigenvectors]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/la_eigenvalues.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
