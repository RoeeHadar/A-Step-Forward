# Curriculum Stream (07)

Repo brief: `.cursor/subagent-briefs/07-curriculum.md`

## Skills (read first)

- [[../../skills/expand-lessons-cursor|expand-lessons-cursor]] → repo `skills/expand-lessons-cursor/SKILL.md`
- [[../../skills/author-lesson|author-lesson]]
- [[../../skills/expand-lesson-theory|expand-lesson-theory]]

## Scope

- `scripts/seed_data/lessons/*.json` (207 lessons)
- `scripts/cursor-expansion-queue.mjs`
- `infra/seeds/**` (legacy YAML course model)

## Acceptance

- Depth + Hebrew parity per expansion policy (2026-07-02)
- Seed via `gh workflow run "Seed DB (one-shot)" -f target=lessons-from-json`

## Vault views

- [[../curriculum/expansion-queue|Expansion queue dashboard]]
- `concepts/` — one note per KG concept
