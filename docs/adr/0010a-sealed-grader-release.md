# ADR 0010a: Sealed Grader-agent release

- **Status:** Accepted (implementation stream)
- **Date:** 2026-07-22
- **Extends:** [ADR-0010](0010-assessment-driven-progression.md)
- **Deciders:** Product owner (grill session 2026-07-22)

## Decision

Learner-visible test scores and per-item feedback are **sealed** until the Grader
agent finishes process review and **releases** a single package. Closed items may
be key-drafted server-side, but mixed tests never reveal partial marks. Linked
teachers review/override after release; gates advance only on released (or
teacher-confirmed) pass. Background cron drains the grade queue so completion
does not depend on the browser tab.

## Consequences

- Supersedes “instant auto score to learner” for open/mixed assessments.
- Fail-closed → `needs_human` (escalate to linked teacher; admin inbox later).
- Notifications on release and on teacher override.
