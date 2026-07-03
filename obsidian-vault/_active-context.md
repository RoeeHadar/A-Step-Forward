---
type: active-context
updated: 2026-07-03
coordinator_status: .cursor/coordinator/STATUS.md
---

# Active Context

> Update this note at the start/end of each focused work session.

## Current focus

- **Stream**: Curriculum / Content (`07-curriculum`)
- **Goal**: Obsidian vault aligned with enriched KG (156 concepts, 0 sparse)
- **Policy**: KG metadata in YAML → `build-kg-json.mjs`; lessons in JSON; vault mirrors both

## Completed (2026-07-03)

- [x] KG sparse enrichment — **156/156** concepts with `skill_atoms` + `level_scope` (YAML source)
- [x] **16** new university concepts (`uni_multivariable` … `uni_quantum_intro`) + aliases to existing lessons
- [x] Vault sync — **156** concept notes, all `data_completeness: full`
- [x] MCP **`asf-obsidian`** connected
- [x] Expansion queue — 207/207 lessons marked done

## KG pipeline (source of truth)

```
content/knowledge-graph/*.yaml
        ↓  node scripts/build-kg-json.mjs
apps/web/src/lib/kg-data.json
        ↓  node scripts/sync-obsidian-concepts.mjs
obsidian-vault/concepts/*.md
```

After YAML edits: run `pnpm vault:build-kg` then `pnpm vault:sync-concepts`.

## Minor follow-ups (non-blocking)

- 8 concepts have **3–4** skill atoms (target was 5–12): `integrals_applications`, `kinematics_2d`, `static_equilibrium`, `doppler`, `optics_physical`, `electric_potential`, `kirchhoff_laws`, `special_relativity`
- `la_matrices` atoms reflect matrix-arithmetic lesson scope, not full linear-systems syllabus
- Lesson JSON `skill_atoms[]` on questions still empty in many files — Postgres mastery wiring is separate

## Links

- [[curriculum/kg-workflow|KG → vault workflow]]
- [[curriculum/expansion-dashboard|Expansion dashboard]]
- [[curriculum/expansion-queue|Expansion queue]]
- [[MCP-ENABLE|MCP enable guide]]
- [[coordination/streams/07-curriculum|Curriculum brief]]
