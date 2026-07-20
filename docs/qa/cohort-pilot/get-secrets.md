# How to get pilot secrets (when needed)

## What we already automated

From `apps/web` (corporate proxy may need TLS bypass):

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
pnpm exec vercel link --yes --project a-step-forward-waij --scope a-step-forward
pnpm exec vercel env pull .env.local --environment production --yes
```

This usually fills **`CLERK_SECRET_KEY`**.  
**`DATABASE_URL`** is often stored as **Encrypted** on Vercel and pulls **empty** — see [get-database-url.md](./get-database-url.md) (one paste from Neon).

## Emails (no real inboxes)

Use Clerk **test** addresses: `asf.pilot.<id>+clerk_test@example.com`  
New-device OTP is always **`424242`** (no email needed).

## Password

Generated into `results/.pilot-password.local` (gitignored). Shared across the 11 pilot accounts.
