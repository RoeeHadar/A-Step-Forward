# Secrets management

## Local

1. Copy `.env.example` → `.env.local` (gitignored)
2. Fill provider keys (Clerk, LLM APIs, etc.)
3. Compose defaults work out of the box for Postgres/Redis/Neo4j/MinIO

Never commit `.env.local`, `.env`, or real API keys.

## CI / staging / production

**Doppler** is the source of truth for non-Vercel secrets:

- Project: `a-step-forward`
- Configs: `stg`, `prd`
- GitHub Actions use `dopplerhq/cli-action` with `DOPPLER_TOKEN`

### Vercel (frontend)

- Dashboard env vars or `vercel env pull`
- Preview envs per PR
- `NEXT_PUBLIC_*` vars are client-visible — no secrets there

### Fly.io (API + services + workers)

```bash
doppler secrets download --no-file --format env | fly secrets import -a asf-api
```

Set per-app: `asf-api`, `asf-memory`, `asf-graphrag`, `asf-orchestrator`, `asf-workers`.

## Sensitive fields at rest

Application code encrypts sensitive memory/note fields with `crypto.envelope` helpers (see security rules). DB credentials and API keys stay in env only.

## Rotation

If a secret appears in a diff or log:

1. Rotate immediately in Doppler / provider
2. Re-import to Fly / Vercel
3. Do not merge the leaking commit
