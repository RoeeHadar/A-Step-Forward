---
concept_id: "ac_circuits"
name: "AC Circuits"
name_he: "מעגלי זרם חילופין"
subject: physics
level: high_school
bagrut_chapter: electricity
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "ac_circuits"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/ac_circuits.json
prerequisites: ["electromagnetic_induction", "simple_harmonic_motion"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# AC Circuits

**HE:** מעגלי זרם חילופין

## Lesson overview

**Lesson:** AC Circuits — Alternating Current
**HE:** מעגלי זרם חילופין (AC)

AC: voltage and current vary sinusoidally. RMS values used for power: $V_{\text{rms}} = V_0/\sqrt{2}$. Transformers step voltage up/down via mutual induction. Inductors and capacitors introduce reactance in AC.

> AC: מתח וזרם סינוסואידיים. ערכי RMS להספק: $V_{\text{rms}} = V_0/\sqrt{2}$. שנאים משנים מתח דרך השראה הדדית. סלילים וקבלים יוצרים ראקטנס ב-AC.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/electromagnetic_induction|electromagnetic_induction]], [[concepts/simple_harmonic_motion|simple_harmonic_motion]]

## Skill atoms

- AC voltage and current: V = V₀·sin(ωt)
- RMS values: V_rms = V₀/√2
- Capacitive reactance: Xc = 1/(ωC)
- Inductive reactance: XL = ωL
- Impedance in RLC circuit
- Resonance in LC circuit
- Power in AC circuits

## Level scope

- **hs_physics:** AC circuits with X_C, X_L, impedance, and LC resonance — advanced electricity material for 5-unit Bagrut. Typical items use V_rms, phasor-style reasoning (sinusoidal sources), and find resonant frequency or power factor conceptually.

## Lesson sections

- **intro:** Why AC?
- **definition:** Key Definitions
- **theory:** RMS, Power, Transformers, Reactance
- **worked_example:** Worked Example 1 — Step-Down Transformer
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — RLC Impedance and Current
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Power Transmission (Exam Level)
- **method_guide:** Method Guide — AC Circuit Problems
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/uni_ac_circuits|uni_ac_circuits]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/ac_circuits.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
