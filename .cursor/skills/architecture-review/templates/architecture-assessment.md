# Architecture Assessment: {{TITLE}}

- **Date:** {{YYYY-MM-DD}}
- **Author:** Architecture Steward (Cursor sub-agent)
- **Status:** Draft | Final
- **Scope:** {{e.g. "Platform overview" | "Plan generation split" | "Chat hot path"}}
- **Related ADRs:** {{links or "none"}}

---

## Executive summary

<!-- 3–5 sentences: current shape, top risk, top recommendation -->

---

## Context & goals

### Questions this review answers

- 

### Explicit non-goals

- 

### Constraints

- Free tier: Vercel + Neon; Render optional
- Auth: Clerk JWT; per-row `learner_id`
- Bilingual HE-default product rules

---

## Current architecture (as-built)

### Container diagram

```mermaid
<!-- paste or link -->
```

### Hot paths traced

| Path | Entry | Stores touched | Sync hops |
|------|-------|----------------|-----------|
| | | | |

### Data ownership

| Entity | Source of truth | Writers | Readers |
|--------|-----------------|---------|---------|
| | | | |

---

## Findings

| ID | Severity | Category | Finding | Evidence | Failure scenario |
|----|----------|----------|---------|----------|------------------|
| F1 | P0–P3 | Coupling / Scale / Race / Ops | | `path:line` or ADR | |

---

## Options analysis

### Theme: {{e.g. "Unify plan generation"}}

| Option | Description | Pros | Cons | Effort | Recommendation |
|--------|-------------|------|------|--------|----------------|
| A | Do nothing | | | | |
| B | Minimal fix | | | | |
| C | Structural change | | | | |

**Recommended:** Option ___ because ___.

---

## Concurrency & consistency notes

- Idempotency:
- Cron / worker overlap:
- Caching / staleness:

---

## Scalability outlook

- **3× traffic:** 
- **10× traffic:** 
- First bottleneck:

---

## Proposed ADRs (if any)

| Proposed ADR | Title | Decision summary |
|--------------|-------|------------------|
| | | |

---

## Sequenced roadmap

1. 
2. 
3. 

### Suggested owners

| Item | Stream / brief |
|------|----------------|
| | `.cursor/subagent-briefs/0X-*.md` |

---

## Verification plan

- [ ] Tests / evals to add
- [ ] Metrics / alerts
- [ ] Rollback procedure

---

## References

- `docs/architecture/current-state.md`
- `PLAN.md`, `ARCHITECTURE.md`
- {{external links used}}
