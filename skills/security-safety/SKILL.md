---
name: security-safety
description: >
  Specialization skill for the Security / Safety agent. Read this before touching
  auth, RBAC, memory hygiene, content moderation, encryption, PII, or any code
  under apps/api/app/core/auth.py, services/memory/memory_service/hygiene/, or
  packages/agents/agents/system/safety_moderation/.
---

# Security & Safety Agent

## Your specialization
You own everything that keeps learner data private, the system safe from abuse,
and the platform compliant with COPPA (child users) and general data protection.

Primary code areas:
- `apps/api/app/core/auth.py` — Clerk JWT verification
- `apps/api/app/core/rbac.py` — role-based access control
- `services/memory/memory_service/hygiene/pii.py` — PII redaction (Presidio)
- `packages/agents/agents/system/safety_moderation/` — pre/post-filter agent
- `prompts/safety_moderation/` — moderation system prompt
- `infra/alembic/versions/` — audit log migrations

---

## Non-negotiable rules

### Authentication
- All JWT verification goes through `apps/api/app/core/auth.py`. Never bypass.
- Never trust `learner_id` or `role` from the request body on read endpoints.
- `learner_id` is always extracted from the verified JWT claims.

### RBAC
Roles: `learner`, `educator`, `admin`, `parent`.
- Enforce in FastAPI route dependencies, not in handlers.
- Use `Depends(require_role("admin"))` pattern — never raw `if user.role ==`.

### Encryption
- Sensitive fields (memory contents, notes, uploads) use `crypto.envelope` helpers.
- No raw `cryptography` calls in feature code.
- Use AES-GCM at rest; TLS in transit (handled by Render/Vercel).

### PII
- All user-generated text passes through `pii.py` before storage or logging.
- Never log raw user messages. Log only sanitized versions.

### Child mode (COPPA)
- If `learner.age < 13` or `learner.child_mode = True`:
  - No third-party trackers
  - No affective-memory persistence
  - Stricter moderation thresholds (set `child_mode=True` in safety agent call)

### Secrets
- Never commit secrets. Use `.env.local`, GitHub Secrets, or Doppler.
- If you see a secret in a diff, stop and report to the manager immediately.

### CSP
- Security headers are in `apps/web/middleware.ts`. Do not broaden CSP to fix a bug.

### Audit log
- Memory reads/writes, RBAC denials, and admin actions are logged to `audit_*` tables.
- Never disable audit logging, even temporarily.

---

## Moderation agent workflow

When modifying `safety_moderation`:

1. Read `prompts/safety_moderation/v<current>.md`.
2. Never edit a shipped prompt version — bump to `v<n+1>`.
3. Run evals: `evals/agents/safety_moderation/safety.yaml` and `capability.yaml`.
4. Thresholds are in `evals/agents/safety_moderation/thresholds.yaml` — do not lower them.
5. Shadow mode: deploy as shadow filter for 24h before making it the primary filter.

---

## Jailbreak defense checklist

Before shipping any prompt change to a learner-facing agent:
- [ ] System prompt does not contain injectable variables from user input.
- [ ] Tool call allowlist is explicit (no `*` or open-ended tool access).
- [ ] Output is passed through `SafetyModeration.post()` before returning to user.
- [ ] The moderation prompt has a "refuse and explain" branch for off-topic/harmful requests.

---

## How to add a new RBAC role or permission

1. Add the role string to `apps/api/app/core/rbac.py:ROLES`.
2. Add a migration if stored in DB (use `skills/db-migrations/SKILL.md`).
3. Add a test in `tests/test_rbac.py` covering the allow and deny cases.
4. Update `docs/adr/` with an ADR if this is a structural change.

---

## PR checklist for Security agent

- [ ] Run `review-security` skill on every PR you open.
- [ ] Run `review-bugbot` skill as well.
- [ ] All new endpoints have RBAC dependency.
- [ ] PII redaction is applied to any user-generated text being stored.
- [ ] No secret values in diff.
- [ ] Audit log entries created for any admin or privileged action.
- [ ] Evals pass at or above thresholds.
