---
type: home
tags:
  - dashboard
updated: 2026-07-03
---

# A Step Forward — Dev Vault

**Primary knowledge base for the monorepo.** Start: [[_active-context|Active context]] · [[CLAUDE|Agent constitution]].

## Status (2026-07-03)

| Metric | Value |
|--------|------:|
| KG concepts | 156 |
| Cross-subject edges | ~93 (`kg-cross-edges.json`) |
| Concept notes | 156 (`data_completeness: full`) |
| Authored lessons | 207 |
| Production web | `e645aa1` (plan-scope mastery + template-only replans) |
| MCP | `asf-obsidian` (Cursor global config) |

## Architecture (read first)

| Topic | Note |
|-------|------|
| **Learning paths & GraphRAG** | [[curriculum/learning-path-architecture|Learning path architecture]] |
| **Cross-subject edges** | [[curriculum/cross-subject-edges|Cross-subject edge authoring]] |
| **Plan & memory (product)** | [[product/plan-and-memory|Plan & memory]] |
| **KG → vault pipeline** | [[curriculum/kg-workflow|KG workflow]] |

## Workflows

| Task | Doc / command |
|------|----------------|
| Edit KG metadata | [[curriculum/kg-workflow|KG → vault]] · `pnpm vault:build-kg` |
| Add math↔physics edge | [[curriculum/cross-subject-edges|Cross-subject edges]] |
| Refresh vault | `pnpm vault:sync` |
| Expansion tracking | [[curriculum/expansion-dashboard|Dashboard]] · [[curriculum/expansion-queue|Queue]] |
| Frontend / plan work | [[coordination/streams/01-frontend|01-frontend stream]] |
| Enable MCP | [[MCP-ENABLE|MCP-ENABLE.md]] |
| Full setup | [[SETUP|SETUP.md]] |

## Concepts by subject

```dataview
TABLE length(rows) AS Count
FROM "concepts"
GROUP BY subject
SORT subject ASC
```

## Expansion status

```dataview
TABLE length(rows) AS Count
FROM "concepts"
GROUP BY expansion_status
SORT expansion_status ASC
```

## Open engineering gaps

See [[curriculum/learning-path-architecture#Known gaps (2026-07-03)|Known gaps]]:

- Unify weekly plan generator with `buildLearningPlan()`
- Time-horizon depth trimming for exam cram
- Golden path defaults per onboarding `goal_key`

## Quick links

- [[coordination/streams/07-curriculum|Curriculum stream]]
- [[coordination/streams/01-frontend|Frontend stream]]
- [[runbooks/scripts-index|Scripts index]]
- [[research/README|Research index]]
- Repo: `.cursor/skills/use-obsidian-vault/SKILL.md`
