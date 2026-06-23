# Resume Briefs — Round 2 (2026-06-23 PM)

These `NN-<stream>-resume.md` files are the **current paste-and-go prompts** for the Composer 2.5 / Cursor Auto sub-agents. They supersede the starter prompts inside the original briefs for this round only. The originals (`NN-<stream>.md`) remain the canonical contract.

## Locked decisions (no need to ask the user)

These defaults are now project policy. Sub-agents must **not** stop to ask the user:

- **Hosting**: web → Vercel, api → Fly.io (region: iad), workers → Fly Machines, Langfuse → self-hosted on Fly.
- **DBs (managed)**: Postgres → Neon (with pgvector), Redis → Upstash, Neo4j → AuraDB Free, object storage → Cloudflare R2 (S3-compatible).
- **Auth**: Clerk (already chosen).
- **Secrets**: Doppler in CI/prod; `.env.local` in dev (see `.env.example`).
- **Domain**: `astepforward.app` if available, else Vercel default `a-step-forward.vercel.app`; Release Captain registers.
- **Branch strategy**: trunk-based on `main`. Each stream stacks its PRs and merges in order. No long-lived branches > 1 week.
- **PRs**: small, atomic, conventional commit titles, required eval gates, `review-bugbot` skill on every PR; `review-security` on auth/memory/RBAC/payments.
- **Repo visibility**: stays `private` until Phase-1 deploy is green; **Release Captain** flips to public when all of: live URL responds, README polished, LICENSE chosen (MIT), security advisories enabled.
- **License**: MIT.
- **Coverage gate**: ≥80% services & agents; ≥70% frontend (`60-testing.mdc`).
- **No flaky tests merged**.
- **If blocked**: open an ADR in `docs/adr/`, pick the safer default, ship a PR, surface the decision in the PR body. **Don't ping the user.**

## How to dispatch a sub-agent this round

1. Open a new Cursor chat on the same workspace.
2. Switch model to **Composer 2.5** (or **Cursor Auto** for routing).
3. Paste the starter prompt from the bottom of the matching `NN-<stream>-resume.md`.
4. Run with `run_in_background: true` if you're spawning several at once.

## End-state acceptance (Release-Captain enforces)

- `apps/web` deployed to Vercel, returns 200 on `/`, learner sign-up works, learner can chat with Tutor.
- `apps/api` deployed to Fly, `/healthz` 200, `/readyz` 200, `/v1/chat` streams Tutor reply.
- Memory writes persist; Dreamer runs nightly; Memory Inspector usable.
- GraphRAG seeded with the Phase-1 course; `kg.hybrid` returns rerank-ed results.
- CI green: `lint-test`, `evals` (touched), `deploy-web`, `deploy-api`, `deploy-workers`.
- Public GitHub repo with polished README, LICENSE, ADRs, SECURITY.md, demo GIF.
- A short marketing landing (`/`) that the user can share on Twitter/X / LinkedIn.

## Stream → resume file

| Stream                | Resume file                                       |
| --------------------- | ------------------------------------------------- |
| Frontend              | `01-frontend-resume.md`                           |
| Backend / API         | `02-backend-api-resume.md`                        |
| Agents framework      | `03-agents-resume.md`                             |
| Memory service        | `04-memory-resume.md`                             |
| GraphRAG              | `05-graphrag-resume.md`                           |
| MCP servers           | `06-mcp-servers-resume.md`                        |
| Curriculum / Content  | `07-curriculum-resume.md`                         |
| Evals & QA            | `08-evals-qa-resume.md`                           |
| Infra / DevOps        | `09-infra-resume.md`                              |
| Security / Safety     | `10-security-safety-resume.md`                    |
| **Release Captain**   | `11-release-captain-resume.md`  ← new this round  |
