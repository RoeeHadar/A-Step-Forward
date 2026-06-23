# ADR-0003 — Security threat model and controls baseline

## Status

Accepted (2026-06-23).

## Context

A Step Forward stores persistent learner memory, routes requests through multiple AI agents, and serves learners of all ages including children under COPPA. We need a documented threat model and a consistent baseline of controls before scaling agent and memory features.

## Decision

1. Adopt the threat model in `docs/security/threat-model.md` as the living security reference.
2. Implement baseline controls in the security stream (sub-agent 10):
   - Clerk JWT verification with JWKS caching and iss/aud validation.
   - RBAC dependency factory + per-row learner policy helpers.
   - PII redaction pipeline (Presidio when available + custom regex rules).
   - SafetyModerationAgent with pre/post hooks on every agent turn.
   - Jailbreak regex fast-path + LLM classifier fallback.
   - COPPA child mode: no affective writes, stricter moderation, CSP tracker restriction.
   - Append-only audit buffers for gateway and memory events + read-only admin endpoints.
   - Security headers (CSP, HSTS, X-Frame-Options, Referrer-Policy) in Next.js middleware.
3. Require `review-security` on PRs touching auth, memory, RBAC, encryption, or payments.

## Consequences

- Security behavior is centralized (auth, rbac, safety, audit) rather than ad-hoc per route.
- Child mode and PII handling are enforceable at memory write time, not only in prompts.
- Residual items (per-learner encryption, parent linkage, WAF) are explicitly tracked in the threat model.
- Security tests must cover auth, RBAC, child mode, PII, and jailbreak paths before merge.

## References

- `PLAN.md` §10–11
- `.cursor/subagent-briefs/10-security-safety.md`
- `docs/security/threat-model.md`
