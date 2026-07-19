---
concept_id: "<%= concept_id %>"
type: lesson-draft
status: draft
target_json: scripts/seed_data/lessons/<%= concept_id %>.json
---

# Draft: <%= concept_id %>

> Staging note — export to JSON when checklist passes. See [[curriculum/goren-geva-checklist|Goren/Geva checklist]].

## intro

<!-- EN prose -->

### intro (HE)

<!-- Hebrew prose — not English paste -->

## definition

## theory

## worked_example (easy)

## checkpoint

## worked_example (medium)

## checkpoint

## worked_example (hard)

## method_guide

## exercise_set

## pitfall

## before_exam

## summary

## Export checklist

- [ ] All sections meet `MIN_WORDS` gates (`.cursor/skills/expand-lessons-cursor/SKILL.md`)
- [ ] `hebrewBodyWeak` false for all sections
- [ ] 8 questions with bilingual explanations (≥80 words each)
- [ ] `agent_hints` updated
- [ ] `node scripts/seed-lessons.mjs --dry-run` passes
- [ ] `node scripts/audit-lesson-depth.mjs --strict --phase=4` passes
