---
concept_id: "distributions"
name: "Probability Distributions"
name_he: "התפלגויות הסתברות"
subject: math
level: high_school
bagrut_chapter: probability
points_levels: ["5pt"]
expansion_status: done
data_completeness: full
lesson_id: "distributions"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/distributions.json
prerequisites: ["combinatorics", "probability_basic"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Probability Distributions

**HE:** התפלגויות הסתברות

## Lesson overview

**Lesson:** Probability Distributions
**HE:** התפלגויות הסתברות

Probability distributions: discrete (binomial, Poisson) and continuous (normal, uniform, exponential). PDF, CDF, mean, variance.

> התפלגויות הסתברות: בדידות (בינומית, פואסון) ורציפות (נורמלית, אחידה, מעריכית). פונקציות PDF, CDF, ממוצע, שונות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/combinatorics|combinatorics]], [[concepts/probability_basic|probability_basic]]

## Skill atoms

- Binomial distribution: P(X=k) = C(n,k)·pᵏ·(1-p)ⁿ⁻ᵏ
- Bernoulli trials (n independent experiments)
- Conditional binomial probability
- Normal distribution (מבוא)
- z-scores and standard normal table
- Using normal table for probability calculations

## Level scope

- **5pt:** Bagrut 5pt probability chapter; binomial + normal distribution

## Lesson sections

- **intro:** What is a probability distribution?
- **definition:** Key Definitions
- **theory:** Key Distributions
- **worked_example:** Worked Example 1 — Uniform Distribution
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Normal Distribution
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Exponential CDF and Percentile (Exam Level)
- **method_guide:** Method Guide — Probability Distributions
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/discrete_distributions_binomial_poisson|discrete_distributions_binomial_poisson]]
- [[concepts/binomial_distribution_bernoulli|binomial_distribution_bernoulli]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/distributions.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
