## Brief

`.cursor/subagent-briefs/11-release-captain-resume.md`

## What & why

Phase-A merge train executed by the Release Captain. Lands three independently
clean stacks onto a single integration branch in priority order:

1. **GraphRAG stack** (`feat/graphrag/01..04`) — kg_chunks ontology migration,
   ingestion pipeline + seed corpus, retrieval modes with Neo4j service,
   KG retrieval evals wired into the CI runner.
2. **Frontend stack** (`feat/frontend/01..09`) — shared `@asf/schemas` (Zod) and
   `@asf/ui` (shadcn primitives) workspace packages, marketing landing + i18n +
   middleware, Clerk auth pages, learner dashboard, streaming agent chat,
   lesson view, Memory Inspector, progress dashboards, educator + admin RBAC
   dashboards. BFF API routes are wired to fixtures until backend Phase-2
   wiring lands (stream 02).
3. **Safety evals** (`feat/security/10-safety-hardening`) — `safety_moderation`
   capability + safety promptfoo matrices.

On top of the merge train, the Release Captain added launch-readiness polish:
`LICENSE` (MIT), `SECURITY.md`, `CHANGELOG.md` + `cliff.toml`, `docs/adr/README.md`
(ADR index), `docs/marketing/*` (landing copy, HN draft, PH draft, social copy),
`docs/diagrams/{architecture,graphrag}.md` (mermaid), `scripts/smoke/{e2e.sh,e2e.ps1}`,
two new CI workflows (`changelog.yml`, `repo-health.yml`), polished `README.md`
with hero block + badges + agent matrix, OG/Twitter metadata in
`apps/web/src/app/layout.tsx`, and `BLOCKED.md` documenting the closed list of
human-only remaining launch steps.

Branches **intentionally not merged**:

- `wip/agents-phase3-snapshot` — Phase-3 agents tangled with workspace
  stabilization; needs surgical split (see `BLOCKED.md` §4).
- MCP stack (`feat/mcp/01..04`, `mcp-stack-base`) — analysis showed net
  deletions vs `main`; the work has already landed on `main` via an earlier
  squash. Branches should be deleted post-merge.

## Acceptance criteria

- [ ] All three merge commits land cleanly with no conflicts (verified locally).
- [ ] `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, `cliff.toml`, `docs/adr/README.md`,
      `BLOCKED.md` present at repo root or `docs/`.
- [ ] `.github/workflows/repo-health.yml` enforces the above on every PR.
- [ ] README renders correctly on github.com with the hero image + badges
      (image must exist at `docs/assets/hero.png`).
- [ ] OG / Twitter cards resolve for `/` on a preview deploy.
- [ ] `review-bugbot` green.
- [ ] `review-security` green (touches `evals/agents/safety_moderation/*` and
      `apps/web/middleware.ts` auth surface).
- [ ] `lint-test.yml` green (web + python jobs).
- [ ] `evals.yml` green (touched-eval gates only).

## Evals

`evals.yml` will run the touched-prompt evals automatically. No prompt content
was changed by this PR — only `evals/agents/safety_moderation/{capability,safety}.yaml`
were added (from the security stack); thresholds in
`evals/agents/safety_moderation/thresholds.yaml` apply.

## Screenshots / GIFs

n/a in this PR — first staging deploy will produce a 30–60s demo GIF to be
dropped at `docs/marketing/demo.gif` and referenced from the README hero
(tracked in `BLOCKED.md` §3).

## Risk / rollback

Low risk: the three stacks touch largely disjoint trees (frontend lives under
`apps/web`/`packages/ui`/`packages/schemas/ts`, GraphRAG under
`services/graphrag`/`infra/alembic`/`evals/retrieval`, safety evals under
`evals/agents/safety_moderation`).

Rollback: revert each merge commit individually (`git revert -m 1 <sha>`) — no
force-push. Order doesn't matter; merges are independent.
