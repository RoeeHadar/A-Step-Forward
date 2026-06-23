# Clerk JWT (production)
# Set CLERK_JWKS_URL to enable Bearer-token auth; omit it for local dev headers.
CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json
CLERK_ISSUER=https://<your-clerk-domain>
CLERK_AUDIENCE=

## Production requirements

- Set `APP_ENV=production` (or `staging` / `preview`) **and** `CLERK_JWKS_URL`. The API refuses to start otherwise.
- RBAC roles (`admin`, `educator`, etc.) are resolved from server-side learner profiles — **not** from JWT `public_metadata`. Assign roles via admin tooling or Clerk webhooks writing to `gateway_users`.
- Never set `DEV_ALLOW_ROLE_HEADERS=true` outside local development.

## Local dev (when CLERK_JWKS_URL is empty)

```bash
curl -H "X-Learner-Id: learner-1" http://localhost:8000/v1/learners/me
```

Optional headers: `X-Role`, `X-Age`, `X-Child-Mode=1` (role headers are ignored unless `DEV_ALLOW_ROLE_HEADERS=true`).
