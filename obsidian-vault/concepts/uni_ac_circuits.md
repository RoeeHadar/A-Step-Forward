---
concept_id: "uni_ac_circuits"
name: "AC Circuits"
name_he: "מעגלי זרם חילופין"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "ac_circuits"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/ac_circuits.json
prerequisites: ["uni_induction", "uni_dc_circuits"]
tags:
  - concept/physics
  - status/todo
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

[[concepts/uni_induction|uni_induction]], [[concepts/uni_dc_circuits|uni_dc_circuits]]

## Skill atoms

- Sinusoidal AC voltage/current and angular frequency ω
- Phasor representation of AC quantities
- Capacitive and inductive reactance X_C, X_L
- Impedance Z in RLC series circuits
- Resonance when X_L = X_C
- Average power in AC circuits

## Level scope

- **physics1:** Intro AC circuits with phasors and impedance; RLC resonance and power factor at university physics-2 bridge depth.

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


## Links

- Lesson JSON: `scripts/seed_data/lessons/ac_circuits.json` _(alias from `uni_ac_circuits`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
