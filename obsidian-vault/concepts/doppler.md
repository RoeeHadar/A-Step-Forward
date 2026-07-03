---
concept_id: "doppler"
name: "Doppler Effect"
name_he: "אפקט דופלר"
subject: physics
level: high_school
bagrut_chapter: radiation
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "doppler"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/doppler.json
prerequisites: ["sound_waves"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Doppler Effect

**HE:** אפקט דופלר

## Lesson overview

**Lesson:** Doppler Effect
**HE:** אפקט דופלר

The Doppler effect for sound and light. Frequency shift when source or observer moves. Formulas and applications.

> אפקט דופלר לגל קול ואור. שינוי תדר בעת תנועת מקור או צופה. נוסחאות ויישומים.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/sound_waves|sound_waves]]

## Skill atoms

- General Doppler: f_obs = f₀(v ± v_obs)/(v ∓ v_src)
- Sign rule: approaching raises observed frequency
- Moving source only: f_obs = f₀·v/(v ∓ v_src)
- Moving observer only: f_obs = f₀·(v ± v_obs)/v
- Both moving: apply numerator and denominator signs together
- Two-frequency method: solve v_src from approach/recession ratio
- Qualitative: approaching source shortens observed wavelength
- Light Doppler approximation: f_obs ≈ f₀(1 ± v/c)

## Level scope

- **hs_physics:** Doppler frequency shift for moving source or observer — a standard radiation-topic calculation. Bagrut questions give speeds and rest frequency and ask for observed frequency or qualitative shift direction (approaching vs receding).

## Lesson sections

- **intro:** Why Does a Siren Change Pitch?
- **definition:** Doppler Formula
- **theory:** Physical Intuition
- **worked_example:** Worked Example 1 — Moving Source
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Moving Observer
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Finding Source Speed from Observed Frequencies
- **method_guide:** Method Guide — Doppler Effect
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away


## Links

- Lesson JSON: `scripts/seed_data/lessons/doppler.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
