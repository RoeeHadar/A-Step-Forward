# Code Review: {{SCOPE}}

- **Date:** {{YYYY-MM-DD}}
- **Reviewer:** Code Reviewer (Cursor sub-agent)
- **Scope:** {{branch name | file list | PR #}}
- **Intent:** {{one sentence — what the change was supposed to do}}
- **Verdict:** SHIP | SHIP WITH WARNINGS | DO NOT SHIP

---

## Summary

<!-- 2–4 sentences: overall quality, main risks, test status -->

---

## Scope reviewed

| Path / area | Notes |
|-------------|-------|
| | |

### Commands run

- [ ] `pnpm --filter @asf/web lint`
- [ ] `pnpm --filter @asf/web exec tsc --noEmit`
- [ ] `vitest` (paths: …)
- [ ] Other: …

---

## Findings

| ID | Sev | Location | Issue | Observable failure | Fix hint |
|----|-----|----------|-------|-------------------|----------|
| R1 | BLOCKER / WARN / NIT | `path:line` | | | |

### Detail (BLOCKER and WARN only)

#### R1 — {{title}}

**Location:** `path:line`

**Issue:** …

**Failure scenario:** …

**Suggested fix:** …

**Owner stream:** 01-frontend | 02-backend-api | …

---

## Silent-function / dead-code audit

| Symbol | Location | Status | Notes |
|--------|----------|--------|-------|
| | | used / dead / unreachable | |

---

## Edge-case matrix

| Case | Handled? | Evidence |
|------|----------|----------|
| `dbConfigured === false` | yes/no | |
| Unauthenticated request | | |
| Empty learner data (new user) | | |
| Concurrent write (same learner) | | |
| Invalid / missing input | | |

---

## Test assessment

| Change area | Tests exist? | Assert behavior? | Gap |
|-------------|--------------|------------------|-----|
| | | | |

---

## Clarity & complexity

<!-- Brief: over-engineering, naming, file size — NITs only unless structural -->

---

## Escalations (other streams)

| Finding ID | Escalate to | Reason |
|------------|-------------|--------|
| | 24-architecture / 10-security / 08-evals | |

---

## Recommended follow-ups

1. 
2. 

---

## References

- Diff / commits: …
- Related assessment: `docs/architecture/assessments/…` (if any)
- Skills: `skills/code-review/SKILL.md`
