# Get DATABASE_URL (only if seeding mid-journey states)

Vercel stores `DATABASE_URL` as **Encrypted**, so CLI pull often returns an **empty** value. Clerk keys usually pull fine.

## Option A — Neon dashboard (easiest)

1. Open https://console.neon.tech and sign in  
2. Open the project used by **A Step Forward** production  
3. **Dashboard → Connection details → Connection string** (URI, include password)  
4. Paste into `apps/web/.env.local` as one line:

```env
DATABASE_URL=postgresql://...
```

Then from repo root:

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
node scripts/seed-cohort-pilot.mjs
```

## Option B — Vercel dashboard

1. https://vercel.com → **a-step-forward** → **a-step-forward-waij**  
2. **Settings → Environment Variables → DATABASE_URL**  
3. Reveal / copy **Production** value  
4. Same paste into `.env.local` as above  

## Verify you got the *production* DB

After pasting, from repo root:

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
node scripts/_list-tables.mjs
```

Expect `learner_profiles true` and dozens of public tables.  
If `table_count 0`, you copied an empty/wrong Neon project — use Vercel’s Production `DATABASE_URL` (Reveal) or the known local file `apps/web/.database-url.local` if present (gitignored).

## Without DATABASE_URL

You can still run the pilot: all students go through **fresh onboarding** (no `building` / `at-risk` / `near-exam` / `day-before` seeds). Mid-journey UX is thinner but identity, lessons, agents, social, and teacher tools still get exercised.
