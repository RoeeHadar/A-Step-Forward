# Architecture Assessments

Structured outputs from the **Architecture Steward** sub-agent.

## Naming

```
YYYY-MM-DD-<kebab-topic>.md
```

Example: `2026-07-05-platform-overview.md`

## Template

Copy from `.cursor/skills/architecture-review/templates/architecture-assessment.md`.

## When to add one

- Platform overview or health check
- Before splitting/merging services or changing SSOT
- After production incidents involving races, coupling, or scale limits
- When proposing ADRs that supersede accepted decisions

Assessments are **informational** until an ADR is accepted or a Coordinator dispatches implementation work.
