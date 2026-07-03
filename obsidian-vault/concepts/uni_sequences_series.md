---
concept_id: "uni_sequences_series"
name: "Sequences & Series"
name_he: "סדרות וטורים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "series_convergence_tests"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/series_convergence_tests.json
prerequisites: ["uni_limits", "uni_integrals"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Sequences & Series

**HE:** סדרות וטורים

## Lesson overview

**Lesson:** Convergence Tests for Series
**HE:** מבחני התכנסות לטורים

Divergence test, integral test, p-series, direct comparison, limit comparison, ratio test, root test, and alternating series (Leibniz). Decision strategy for choosing the right test.

> מבחן הגבול, מבחן האינטגרל, טורי p, השוואה ישירה, השוואת גבולות, מבחן המנה, מבחן השורש ומבחן לייבניץ לטורים מתחלפים. אסטרטגיית בחירת המבחן המתאים.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_limits|uni_limits]], [[concepts/uni_integrals|uni_integrals]]

## Skill atoms

- Divergence test: lim aₙ≠0 ⇒ series diverges (converse false)
- p-series convergence: Σ1/nᵖ converges iff p>1
- Integral test for positive decreasing terms
- Direct comparison test (termwise inequality)
- Limit comparison test with reference series
- Ratio test for factorials and exponential powers
- Root test for nth-power terms
- Alternating series (Leibniz): bₙ decreasing and lim bₙ=0
- Absolute vs conditional convergence classification
- Convergence test decision strategy (which test to try first)

## Level scope

- **calc1:** Late calc-1 / early calc-2 bridge; aliased lesson covers full convergence-test toolkit — Israeli university finals typically include 2–3 series classification problems.

## Lesson sections

- **intro:** Why Convergence Matters
- **definition:** Convergence, Divergence, and the Main Tests
- **theory:** Key Intuitions
- **worked_example:** Worked Example 1 — p-Series Test
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Ratio Test with Factorials
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Conditional vs Absolute Convergence
- **method_guide:** Method Guide — Which Convergence Test to Use
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/series_convergence_tests.json` _(alias from `uni_sequences_series`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
