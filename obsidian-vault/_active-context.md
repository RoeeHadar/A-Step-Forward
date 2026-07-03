# Active Context — KG sparse enrichment (COMPLETE)

**Date:** 2026-07-03  
**Status:** ✅ Done — **0 kg-sparse** in vault sync (140 full / 16 syllabus-only)

## Workers (all complete)
| Worker | File | Result |
|--------|------|--------|
| W1 | `math-university.yaml` | 15 concepts — la_* + uni_* calc |
| W2 | `physics-university.yaml` | 9 uni_* physics (`physics1` level) |
| W3 | `physics-high-school.yaml` | 35 HS physics — `level_scope.hs_physics` only |
| W4 | `math-high-school.yaml` | 40 bagrut-split + stats concepts |

## Verification (coordinator)
- `node scripts/build-kg-json.mjs` → **156 concepts**
- `node scripts/sync-obsidian-concepts.mjs` → **full=140, kg-sparse=0, syllabus-only=16**
- Original **99 mission IDs** → all resolve to full KG entries (direct or via alias)

## Out of scope (syllabus-only, no lesson)
16 advanced uni concepts: `uni_multivariable` … `uni_quantum_intro` — no authored lesson; expect 0 new lessons.

## Not committed
Awaiting user request.

## Known follow-ups (non-blocking)
- `la_matrices` atoms reflect matrix-arithmetic lesson, not full linear-systems coverage
- `uni_sequences_series` lesson tagged calc2 vs KG calc1 placement
- Lesson JSON `skill_atoms[]` still empty in many files — Postgres mastery wiring is separate
