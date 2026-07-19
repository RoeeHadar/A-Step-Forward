---
type: runbook
tags:
  - curriculum/kg
  - graphrag
updated: 2026-07-03
---

# Cross-Subject Edge Authoring

Hand-curated edges live in `apps/web/src/lib/kg-cross-edges.json`. The path planner merges these with within-subject `prerequisites[]` from [[kg-workflow|KG YAML]].

Repo skill: `.cursor/skills/cross-subject-kg/SKILL.md`.

## When to add an edge

| Situation | Relation | Example |
|-----------|----------|---------|
| Learner literally cannot understand B without A | `prereq` | `vectors_basics → kinematics_2d` |
| A is a mathematical tool used inside B | `applies_to` | `functions_quadratic → kinematics_1d` |
| A is the general principle; B is the instance | `generalizes` | `derivatives_intro → newton_laws` |
| B is modeled by A | `models` | `differential_equations → simple_harmonic_motion` |
| A is computational support for B | `tooling_for` | `la_matrices → kinematics_2d` |

## Workflow

1. Verify both `src` and `dst` exist in `kg-data.json` (check vault `concepts/<id>.md`)
2. Add edge to `kg-cross-edges.json` (group with related edges in file)
3. Re-seed: `gh workflow run "Seed DB (one-shot)" -f target=lessons` (upserts `kg_edges`)
4. Probe: `GET /api/learning-plan/next?goal=<dst>` as logged-in user — edge should appear in `path[]`

## Weight guidance

| Weight | Use |
|--------|-----|
| `1.0` | Hard dependency — always walk for long horizons |
| `0.7–0.9` | Strong enabler — include unless cram + no failure signal |
| `0.4–0.6` | Soft tooling — skip on short exam horizons unless mastery low |

## Pitfalls

- ❌ Edge to non-existent concept id — seeder warns, does not fail
- ❌ Cycles — planner terminates but model is wrong; refactor
- ❌ Duplicate atom names per subject — reuse one atom across lessons
- ❌ Writing directly to Neon `kg_edges` — JSON is source of truth

## High-value math → physics examples (in corpus)

| Math | Physics | Note |
|------|---------|------|
| `functions_quadratic` | `kinematics_1d` | Parabolic motion |
| `derivatives_intro` | `kinematics_1d`, `newton_laws` | v = dx/dt, F = m dv/dt |
| `integrals_intro` | `work_energy`, `kinematics_1d` | W = ∫F·dx, x = ∫v dt |
| `trigonometry_ratios` | `kinematics_2d`, `projectile_motion` | Component decomposition |
| `trigonometry_identities` | `ac_circuits`, `simple_harmonic_motion` | Phasors, sinusoids |

Full list: `apps/web/src/lib/kg-cross-edges.json`.

## Related

- [[learning-path-architecture|Learning path architecture]]
- [[kg-workflow|KG → vault workflow]]
