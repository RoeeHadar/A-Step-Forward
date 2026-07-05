# Stream 24 — Architecture Steward

**Cursor sub-agent** for platform/system architecture review (not product learning-path design).

## Brief & skill

| Resource | Path |
|----------|------|
| Sub-agent brief | `.cursor/subagent-briefs/24-architecture-steward.md` |
| Primary skill | `skills/architecture-review/SKILL.md` |
| Checklists | `skills/architecture-review/REFERENCE.md` |
| As-built snapshot | `docs/architecture/current-state.md` |
| Assessments | `docs/architecture/assessments/` |

## Scope

- Monolith vs subservices, coupling, scalability, races, data ownership
- ADR proposals (Proposed only — Opus accepts)
- Cross-stream recommendations with sequenced owners

## Out of scope

- [[learning-path-architecture|Learning path product architecture]] (stream 07 / brief 14)
- Feature implementation unless ADR accepted + Coordinator dispatch

## Status

| Date | Assessment | Outcome |
|------|------------|---------|
| 2026-07-05 | Groundwork shipped | Skill, brief, `current-state.md`, template |
| 2026-07-05 | [Platform overview](../../docs/architecture/assessments/2026-07-05-platform-overview.md) | Coordinator implemented items 1–3; ADR 0006/0007 proposed; planner unification deferred to stream 07 |

## Open review queue

1. [x] Platform overview assessment
2. [ ] Dual planner unification (ADR-0007 → stream 07)
3. [ ] Chat hot-path latency & failure isolation
4. [x] Cron/worker idempotency (advisory lock + single cron owner)

## Links

- [[../_active-context|Active context]]
- ADRs: `docs/adr/README.md`
