---
type: dashboard
tags:
  - curriculum/expansion
  - dashboard
---

# Expansion Dashboard

> Requires **Dataview** plugin. Regenerate: `pnpm vault:sync`

## KG health (2026-07-03)

All **156** concept notes should show `data_completeness: full`. Workflow: [[kg-workflow|KG → vault]].

```dataview
TABLE length(rows) AS Count
FROM "concepts"
GROUP BY data_completeness
SORT data_completeness ASC
```

## Expansion status

See [[expansion-queue|Expansion queue]] for commands. Corpus: **207/207** lessons marked done.

```dataview
TABLE length(rows) AS Count
FROM "concepts"
GROUP BY expansion_status
SORT expansion_status ASC
```

## By subject

```dataview
TABLE length(rows) AS Concepts
FROM "concepts"
GROUP BY subject
SORT subject ASC
```

## By level

```dataview
TABLE length(rows) AS Concepts
FROM "concepts"
GROUP BY level
SORT level ASC
```

## Not expanded (todo / in-progress)

```dataview
TABLE data_completeness, name, lesson_id
FROM "concepts"
WHERE expansion_status != "done"
SORT expansion_status ASC, name ASC
```

## University track (`uni_*`)

```dataview
TABLE expansion_status, lesson_id, lesson_aliased
FROM "concepts"
WHERE startswith(concept_id, "uni_")
SORT concept_id ASC
```

## Recently synced

```dataview
TABLE expansion_status, subject, file.mtime AS modified
FROM "concepts"
SORT file.mtime DESC
LIMIT 15
```

## Quick links

- [[kg-workflow|KG → vault workflow]]
- [[expansion-queue|Expansion queue (generated)]]
- [[goren-geva-checklist|Goren/Geva checklist]]
- [[../coordination/streams/07-curriculum|Curriculum brief]]
