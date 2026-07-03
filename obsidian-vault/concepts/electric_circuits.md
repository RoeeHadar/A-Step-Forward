---
concept_id: "electric_circuits"
name: "Electric Circuits"
name_he: "מעגלי חשמל (DC)"
subject: physics
level: high_school
bagrut_chapter: electricity
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "electric_circuits"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/electric_circuits.json
prerequisites: ["electric_potential"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Electric Circuits

**HE:** מעגלי חשמל (DC)

## Lesson overview

**Lesson:** Electric Circuits: Ohm's Law, Resistors, and Kirchhoff's Laws
**HE:** מעגלים חשמליים: חוק אוהם, נגדים, וחוקי קירכהוף

Ohm's law $V=IR$ relates voltage, current, and resistance. Resistors in series add; parallel resistors give a smaller equivalent. Kirchhoff's laws solve complex circuits. Power $P=IV$.

> חוק אוהם $V=IR$ מקשר מתח, זרם והתנגדות. נגדים בטור מסתכמים; נגדים במקביל נותנים התנגדות קטנה יותר. חוקי קירכהוף פותרים מעגלים מסובכים. הספק $P=IV$.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/electric_potential|electric_potential]]

## Skill atoms

- Electric current: I = Q/t
- Ohm's law: V = IR
- Resistors in series: R_total = ΣRᵢ
- Resistors in parallel: 1/R_total = Σ(1/Rᵢ)
- EMF and internal resistance
- Power: P = IV = I²R = V²/R
- Energy: E = Pt
- Ammeter and voltmeter placement

## Level scope

- **hs_physics:** DC circuit fundamentals — Ohm's law, series/parallel resistors, EMF with internal resistance, and P = IV. Almost every electricity exam includes a circuit calculation with ammeter/voltmeter placement and power/energy sub-parts.

## Lesson sections

- **intro:** Why Circuit Analysis Matters
- **definition:** Ohm's Law, Series, Parallel, and Power
- **theory:** Applying Kirchhoff's Laws and Internal Resistance
- **worked_example:** Worked Example 1 — Series Resistors
- **checkpoint:** Stop & Practice — Easy
- **worked_example:** Worked Example 2 — Parallel Resistors: Total Current and Power
- **checkpoint:** Stop & Practice — Medium
- **worked_example:** Worked Example 3 — Wheatstone Bridge: Find Unknown Resistance
- **method_guide:** Step-by-Step Approach for Circuit Problems
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes in Circuit Analysis
- **why_matters:** Why it matters
- **before_exam:** Exam Preparation — Electric Circuits
- **summary:** Summary — Key Equations


## Links

- Lesson JSON: `scripts/seed_data/lessons/electric_circuits.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
