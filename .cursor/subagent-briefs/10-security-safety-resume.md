# 10 — Security / Safety — Resume Brief (Round 2)

## Current state

You've barely started. On `feat/security/10-safety-hardening` (2 files, 80 lines):
- `evals/agents/safety_moderation/capability.yaml`
- `evals/agents/safety_moderation/safety.yaml`

`safety_moderation/thresholds.yaml` lives on `main`. The agent itself is a stub on `main`; the rest of safety/security is scaffolded in `packages/agents/agents/base/safety.py`.

## What's left

This stream is critical — block PR merges until done in the right order:

1. **Real `safety_moderation` agent**: stream 03 implements the agent class; you own the prompt + thresholds + classifier choice + the pre/post wiring on every learner-facing agent.
2. **Jailbreak defense**: pre-classifier (regex + Llama-Guard-3 / OpenAI moderation hybrid). Tag `prompt_injection_score`, `pii_score`, `toxicity_score`. Block above threshold, log all to `audit_safety_events`.
3. **PII redaction**: Presidio + custom en/he recognizers — owned by stream 04 (Memory); you provide the recognizer list + thresholds + the test corpus.
4. **Clerk JWT verification + JWKS cache + RBAC** (owned by stream 02; you review). Add `apps/api/app/core/rbac.py` policy helpers: `require_role`, `require_self_or_role`, `assert_learner_owns(memory_id)`.
5. **Per-row policy**: `learner_id` from auth context only. Tests that prove cross-learner reads are denied.
6. **Child Mode** (COPPA): if `learner.age < 13` OR `learner.child_mode = true`:
   - No affective-memory persistence.
   - Stricter moderation thresholds.
   - No third-party trackers (frontend coord with stream 01).
   - Education-grade content filters.
7. **CSP + security headers** in `apps/web/middleware.ts`: deny-by-default, allowlist Clerk/Anthropic/Sentry origins. Coord with stream 01.
8. **Audit logging**: `audit_memory_events`, `audit_safety_events`, `audit_admin_actions` — Postgres-backed; read-only admin endpoint.
9. **AES-GCM envelope encryption** for sensitive fields (memory contents, notes, uploads). Add `packages/crypto/` helpers; refuse raw `cryptography` in feature code.
10. **Secret scanning**: pre-commit + CI (`gitleaks`). Add to `.github/workflows/lint-test.yml`.
11. **Dependency scanning**: `pip-audit` + `npm audit` in CI; block on `high`.
12. **SECURITY.md** + responsible disclosure email + GH security advisories enabled.
13. **`review-security` skill** required on PRs touching auth/memory/graphrag/mcp/payments/RBAC/encryption (rule `80-pr-style.mdc`).

## Locked decisions

- Clerk for auth.
- Presidio for PII (en + he initial).
- Llama-Guard-3 (or OpenAI Moderation as fallback) for safety classification.
- AES-GCM envelope encryption via `packages/crypto/`.
- License: MIT.
- Child-mode default true if age unknown.

## Done when

- Every learner-facing agent passes through `SafetyModeration.pre/post`.
- RBAC tests cover deny-by-default + cross-learner isolation.
- CSP locked + secret scanning + dep scanning in CI.
- `audit_*` tables exist and are written-to in production paths.
- SECURITY.md + advisories live.
- `review-security` enforced on the scoped PRs.
- Penetration smoke test: a script under `scripts/security/smoke.sh` runs OWASP-zap baseline against staging.

## Required reading

- `PLAN.md` §9; `ARCHITECTURE.md` §9.
- `.cursor/rules/50-security.mdc`, `40-memory-rules.mdc`, `30-agent-authoring.mdc`.
- `.cursor/subagent-briefs/10-security-safety.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Security/Safety sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/10-security-safety-resume.md
  3. .cursor/subagent-briefs/10-security-safety.md
  4. PLAN.md §9; ARCHITECTURE.md §9
  5. .cursor/rules/{30,40,50}-*.mdc

Then, in priority order:
  A. Coordinate with stream 03 to ship the real safety_moderation agent;
     you author the prompt + thresholds + classifier choice + the pre/post
     wiring on every learner-facing agent.
  B. Pre-classifier jailbreak defense (regex + Llama-Guard-3 / OpenAI Mod
     fallback) with audit_safety_events logging.
  C. Coordinate with stream 04 to ship Presidio en/he PII recognizers + test corpus.
  D. Coordinate with stream 02 to ship Clerk JWT verification + RBAC helpers in
     apps/api/app/core/rbac.py; tests for cross-learner isolation.
  E. Implement Child Mode policies end-to-end (coord streams 01 + 04).
  F. CSP + security headers in apps/web/middleware.ts (coord stream 01).
  G. Postgres-backed audit_* tables + admin read endpoint.
  H. packages/crypto/ AES-GCM envelope helpers; ban raw `cryptography` in features.
  I. gitleaks + pip-audit + npm audit in CI (lint-test.yml).
  J. SECURITY.md + GH advisories enabled.
  K. scripts/security/smoke.sh — OWASP zap baseline against staging.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. review-bugbot AND review-security on each of your PRs.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: deployed website is safe to publish to real children/learners —
every auth, PII, jailbreak, CSP, audit, and dep gate green.
```
