---
type: dashboard
tags:
  - curriculum/expansion
  - dashboard
---

# Expansion Dashboard

> Requires **Dataview** plugin. Regenerate queue: `node scripts/sync-obsidian-expansion.mjs`

## Summary

See [[expansion-queue|Expansion queue]] for the full priority table and commands.

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

## Not done (todo / in-progress / qa-gap)

```dataview
TABLE expansion_status, data_completeness, name, subject
FROM "concepts"
WHERE expansion_status != "done"
SORT expansion_status ASC, name ASC
```

## Syllabus-only (no lesson JSON, even via alias)

```dataview
TABLE name, level, lesson_id
FROM "concepts"
WHERE data_completeness = "syllabus-only"
SORT level ASC, name ASC
```

## KG sparse (lesson exists; enrich kg-data.json)

```dataview
TABLE lesson_id, name, subject
FROM "concepts"
WHERE data_completeness = "kg-sparse"
SORT subject ASC, name ASC
LIMIT 25
```

## Recently synced concept notes

```dataview
TABLE expansion_status, subject, file.mtime AS modified
FROM "concepts"
SORT file.mtime DESC
LIMIT 15
```

## Quick links

- [[expansion-queue|Expansion queue (generated)]]
- [[goren-geva-checklist|Goren/Geva checklist]]
- [[../coordination/streams/07-curriculum|Curriculum stream brief]]
- Repo skill: `skills/expand-lessons-cursor/SKILL.md`
