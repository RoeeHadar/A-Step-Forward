# PR5 — Bagrut 372 / pilot content coverage audit

**Date:** 2026-07-11  
**Pilot default:** New Bagrut curriculum (372 / 471 / 572 tracks)

## Math 372 (new 3pt) — `MATH_3PT_NEW_CONCEPTS`

| Status | Count | Notes |
|--------|-------|-------|
| Authored lesson JSON | 21/24 direct filenames | All 372-new topics have lessons |
| Catalogue-only IDs | 3 | `descriptive_statistics`, `basic_probability`, `normal_distribution_basics` |

The three catalogue-only IDs **resolve via `concept-aliases.ts`** to existing lessons:

| Catalogue ID | Authored lesson |
|--------------|-----------------|
| `descriptive_statistics` | `statistics_descriptive` |
| `basic_probability` | `probability_basic` |
| `normal_distribution_basics` | `descriptive_stats` |

**Pilot verdict:** 372 new track is **content-complete** for in-house corpus (no new JSON required for pilot).

### 372-specific tagging (PR5)

These lessons carry `math_track: ["3pt"]` for quiz/planner filtering:

- `linear_programming_two_variables`
- `quadratic_model_fitting`
- `spatial_reasoning`
- `3d_solids_volume`
- `basic_statistics_3pt`, `probability_basics_3pt`, `probability_conditional_3pt`, `linear_regression_3pt`

## Bagrut 4pt / 5pt

Dedicated track lessons exist (`*_4pt`, `*_5pt`, `function_analysis_*`). Catalogue concepts without dedicated JSON typically alias to KG nodes or sibling lessons — see `concept-aliases.ts`.

**Not blocking pilot:** uni-only gaps (e.g. `photoelectric_effect` → `modern_physics_intro` alias).

## Bagrut physics

- Mechanics / electricity / optics corpus: ~54 lessons
- **Lab section** (`high_school_physics` lab chapter): `concept_ids: []` in catalogue — **out of pilot scope** until lab JSON authored

## Follow-up (Phase 2 content)

- Dedicated JSON files for alias-only 372 IDs (optional — reduces indirection)
- Physics lab concept pack
- `function_analysis_4pt` / `_5pt` as KG nodes or aliases in `kg-data.json`
