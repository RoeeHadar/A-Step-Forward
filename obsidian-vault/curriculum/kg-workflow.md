---
type: runbook
tags:
  - curriculum/kg
---

# KG → Obsidian Workflow

## Source of truth

| Layer | Location | Edit when |
|-------|----------|-----------|
| **KG metadata** | `content/knowledge-graph/*.yaml` | Adding skill atoms, level scope, prerequisites, new concepts |
| **Cross-subject edges** | `apps/web/src/lib/kg-cross-edges.json` | Math↔physics enablers — see [[cross-subject-edges|cross-subject runbook]] |
| **Compiled KG** | `apps/web/src/lib/kg-data.json` | **Generated** — do not hand-edit (overwritten on build) |
| **Path planner** | `apps/web/src/lib/learning-plan.ts` | Mastery-aware backward walk — see [[learning-path-architecture|architecture]] |
| **Lesson corpus** | `scripts/seed_data/lessons/*.json` | Authoring bilingual lesson content |
| **Concept ↔ lesson map** | `apps/web/src/lib/concept-aliases.ts` | Syllabus id differs from lesson filename |
| **Vault notes** | `obsidian-vault/concepts/*.md` | **Generated** — user content only under `## Expansion notes` |

### YAML files

| File | Domain |
|------|--------|
| `math-university.yaml` | `uni_*` calc, `la_*` linear algebra |
| `physics-university.yaml` | `uni_*` physics |
| `math-high-school.yaml` | Bagrut math splits, statistics |
| `physics-high-school.yaml` | Bagrut physics |
| _(others in dir)_ | Remaining HS math / cross-subject |

## Commands

```bash
# After editing YAML
pnpm vault:build-kg

# Refresh vault concept notes (preserves ## Expansion notes)
pnpm vault:sync-concepts

# Full vault refresh
pnpm vault:sync

# Expansion queue dashboard only
pnpm vault:sync-expansion
```

## Frontmatter on concept notes

| Field | Meaning |
|-------|---------|
| `data_completeness: full` | KG has skill_atoms + level_scope |
| `data_completeness: kg-sparse` | Lesson linked but KG metadata empty — **should be 0** after enrichment |
| `data_completeness: syllabus-only` | No resolvable lesson JSON — **should be 0** with current aliases |
| `lesson_aliased: true` | `concept_id` ≠ `lesson_id`; see `concept-aliases.ts` |
| `expansion_status` | From expansion progress file + lesson presence |

## Adding a new KG concept

1. Add entry to the appropriate `content/knowledge-graph/*.yaml`
2. If lesson id differs, add alias in `concept-aliases.ts`
3. `pnpm vault:build-kg && pnpm vault:sync-concepts`
4. Open `obsidian-vault/concepts/<id>.md` — verify skill atoms, lesson overview, sections

## Related

- [[learning-path-architecture|Learning path architecture]]
- [[cross-subject-edges|Cross-subject edges]]
- Skill: `.cursor/skills/use-obsidian-vault/SKILL.md`
- Skill: `.cursor/skills/cross-subject-kg/SKILL.md`
- [[expansion-dashboard|Expansion dashboard]]
- [[../runbooks/scripts-index|Scripts index]]
