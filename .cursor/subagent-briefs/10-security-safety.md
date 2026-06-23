# 10 — Security & Safety

## Goal
Harden A Step Forward across auth, data, prompts, and abuse. Implement the safety/moderation agent, jailbreak defenses, COPPA-aware child mode, PII handling, RBAC, and audit logging.

## In-scope files
- `apps/api/app/core/auth.py`, `apps/api/app/core/rbac.py`
- `services/memory/memory_service/hygiene/pii.py` (in coordination with 04)
- `packages/agents/agents/system/safety_moderation/**`
- `apps/web/middleware.ts` (CSP, headers)
- `infra/alembic/versions/**` (audit tables)

## Out-of-scope
- Implementing the rest of the agents (03).

## Deliverables
1. Clerk JWT verification + JWKS caching.
2. RBAC dependency factory + per-row policy helpers.
3. PII pipeline (Presidio + custom rules + `services/memory` integration).
4. Safety / Moderation agent with pre and post hooks for every agent call.
5. Jailbreak input classifier (small fast model + rules); refusal templates.
6. Child mode policy: COPPA-aware, no affective storage, stricter thresholds, no third-party trackers.
7. Audit log tables + read-only admin endpoint.
8. CSP, HSTS, X-Frame-Options, Referrer-Policy in `middleware.ts`.
9. Threat model document `docs/security/threat-model.md`.

## Required reading
1. `PLAN.md` §10, §11.
2. `.cursor/rules/50-security.mdc`, `40-memory-rules.mdc`, `30-agent-authoring.mdc`.

## Acceptance criteria
- Security tests cover auth, RBAC, child-mode, PII leaks, jailbreak attempts.
- `review-security` skill passes for every PR touching auth/memory/payment.
- Audit log captures memory R/W, RBAC denials, admin actions, model overrides.
- Threat model reviewed and ADR recorded.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§10, §11),
  .cursor/rules/50-security.mdc, 40-memory-rules.mdc, 30-agent-authoring.mdc,
  .cursor/subagent-briefs/10-security-safety.md (this file).
Implement the deliverables in order. Coordinate with 02 (auth in API) and 04 (PII in memory).
Run review-security on every PR you open.
```
