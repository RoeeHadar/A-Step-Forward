---
concept_id: "<%= concept_id %>"
name: "<%= name %>"
name_he: "<%= name_he %>"
subject: "<%= subject %>"
level: "<%= level %>"
bagrut_chapter: "<%= bagrut_chapter %>"
points_levels: [<%= points_levels %>]
expansion_status: todo
lesson_json: scripts/seed_data/lessons/<%= concept_id %>.json
prerequisites: [<%= prerequisites %>]
tags:
  - concept/<%= subject %>
  - status/todo
---

# <%= name %>

**HE:** <%= name_he %>

## Prerequisites

<%= prereq_links %>

## Skill atoms

<%= skill_atoms %>

## Level scope

<%= level_scope %>

## Links

- Lesson JSON: `scripts/seed_data/lessons/<%= concept_id %>.json`
- Research: [[research/bagrut-math-research|Bagrut math]] · [[research/bagrut-physics-research|Bagrut physics]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, QA feedback -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
