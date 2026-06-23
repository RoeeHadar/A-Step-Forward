# Security Policy

A Step Forward handles learner data, including children under 13 (with COPPA-aware
policies). Security and privacy are first-class concerns. The full threat model
lives in [`docs/security/threat-model.md`](docs/security/threat-model.md).

## Supported versions

Until 1.0, only the latest tagged release and the current `main` receive security
fixes.

| Version | Supported |
| ------- | --------- |
| `main` / latest tag | yes |
| any older tag | no |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security reports.**

Email: **security@astepforward.app** (set up at launch; until then, use
`roee.hadar+security@gmail.com`).

PGP key: published at `/.well-known/security.txt` after first prod deploy.

Include:

- a brief description of the issue,
- a proof-of-concept or minimal reproduction,
- the impact you believe it has,
- any fix idea you'd like to suggest.

We aim to:

- acknowledge within **48 hours**,
- triage and provide an initial severity within **5 business days**,
- ship a fix or mitigation for **critical** issues within **14 days**.

We follow [coordinated disclosure](https://www.cisa.gov/coordinated-vulnerability-disclosure-process)
and will credit reporters in the changelog and release notes unless you ask us
not to.

## Scope

In scope:

- All code in this repository (`apps/web`, `apps/api`, `services/*`, `packages/*`,
  `mcp-servers/*`, `infra/*`).
- The deployed `astepforward.app` (or current production) domain and its
  subdomains operated by the project.
- The Memory and GraphRAG services and any data they persist.
- Authentication / RBAC enforcement (Clerk + per-row policies).

Out of scope:

- Third-party services we depend on (Clerk, Vercel, Fly.io, Neon, Upstash,
  Cloudflare, Anthropic, OpenAI, Voyage, Cohere, Sentry, Langfuse). Please
  report those upstream.
- Social engineering, physical attacks, or denial-of-service tests against
  production.
- Automated scanning that generates significant load against production. Use a
  preview deployment instead — open an issue requesting a preview URL.

## Privacy & data handling

- All learner data is encrypted at rest with **AES-GCM** envelope encryption via
  `crypto.envelope` helpers; no raw `cryptography` calls in feature code.
- PII is redacted before any storage or log via
  `services/memory/memory_service/hygiene/pii.py` (Presidio + custom rules).
- Learners under 13 (or with `learner.child_mode = true`) get COPPA-aware
  treatment: no third-party trackers, no affective-memory persistence, stricter
  moderation thresholds.
- Memory reads/writes, RBAC denials, and admin actions are logged to `audit_*`
  tables.

## Hardening reference

See [`.cursor/rules/50-security.mdc`](.cursor/rules/50-security.mdc) for the
in-repo security rule that every contributor (human or AI sub-agent) must follow.
