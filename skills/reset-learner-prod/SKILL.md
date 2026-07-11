---
name: reset-learner-prod
description: >
  Full or partial wipe of a learner's Neon data on production (plans, memory,
  chat, mastery, onboarding profile). Use when the user asks to reset their
  account, start fresh for pilot testing, clear a plan before re-testing
  onboarding/Memory/Progress/Coach, or when an agent must reset roeehadar@gmail.com
  (or another Clerk user) on https://a-step-forward-waij.vercel.app.
---

# Reset learner (production)

## What gets cleared

| Mode | Clears | Keeps | After reset |
|------|--------|-------|-------------|
| **Full** (`full: true`) | chat, agent notes, mastery, skill practice, plans, diagnostic sessions, **onboarding profile** | Clerk account only | `/onboarding` |
| **Partial** (legacy) | same except profile row | goal, subjects, exam dates | plan may regenerate identically |

**Default for pilot testing:** always **full** reset.

Implementation: `resetLearnerData()` in `apps/web/src/lib/neon-db.ts`, `POST /api/learner/reset-data`.

---

## Path 1 — User self-service (simplest, no agent)

While signed in on production:

1. **Settings → Persona** (`/settings/persona`)
2. Danger zone → **Reset everything**
3. Confirm → redirected to `/onboarding`

**Browser console** (same session):

```javascript
fetch('/api/learner/reset-data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ full: true }),
})
  .then((r) => r.json())
  .then(console.log);
window.location.href = '/onboarding';
```

---

## Path 2 — Agent ops script (roee / any user)

### Prerequisites

- `DATABASE_URL` on **Vercel Production** and **GitHub `secrets.DATABASE_URL`** must be the **same** Neon database.
- `CLERK_SECRET_KEY` in `apps/web/.env.local` (for `--email` lookup).
- Windows: use `npx.cmd`, not `npx` (PowerShell execution policy).

**Trap:** `vercel env run` loads `apps/web/.env.local` **after** cloud env and **overrides** `DATABASE_URL`. If local points at a different Neon host than Vercel runtime, scripts wipe the wrong DB. Verify host:

```powershell
cd apps/web
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
npx.cmd vercel env run --environment production -- node -e "console.log(new URL(process.env.DATABASE_URL||'').hostname||'MISSING')"
```

If `MISSING` without `.env.local`, cloud var is unset — set it in Vercel dashboard first.

### Full reset by email

```powershell
cd <repo-root>
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
$env:DATABASE_URL = '<paste production Neon URL — never commit>'
node scripts/reset-learner.mjs --email roeehadar@gmail.com --delete-profile
```

### Full reset by Clerk user id

```powershell
node scripts/reset-learner.mjs --user-id user_3FakzyAcsPAfzap2ule6sVHNahk --delete-profile
```

(`roeehadar@gmail.com` → `user_3FakzyAcsPAfzap2ule6sVHNahk` as of 2026-07.)

### Verify

```powershell
cd apps/web
npx.cmd vercel env run --environment production -- node ../../scripts/check-learner-state.mjs user_3FakzyAcsPAfzap2ule6sVHNahk
```

Expect all counts **0**. Schema smoke:

```powershell
npx.cmd vercel env run --environment production -- node ../../scripts/verify-neon-schema.mjs
```

Expect `tables_ok: yes`.

---

## Path 3 — Agent via Vercel env (no manual URL paste)

When `.env.local` already has the **correct production** `DATABASE_URL`:

```powershell
cd apps/web
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
npx.cmd vercel env run --environment production -- node ../../scripts/reset-learner.mjs --email roeehadar@gmail.com --delete-profile
```

Save URL to a local file (clipboard piping fails on Windows):

```powershell
npx.cmd vercel env run --environment production -- node -e "require('fs').writeFileSync('.database-url.local', process.env.DATABASE_URL||'MISSING'); console.log('written');"
```

File is gitignored. Delete after use.

---

## DATABASE_URL / Neon sync (when reset “does nothing”)

1. Vercel → project **a-step-forward-waij** → **Settings → Environment Variables** → `DATABASE_URL` → **Edit** (cannot reveal; only replace).
2. GitHub → repo **Secrets → Actions** → `DATABASE_URL` → same string.
3. **Redeploy** Vercel production after env change.
4. Optional: `gh workflow run wire-vercel-env.yml` (pushes GitHub secrets → Vercel).

If web tables missing (`chat_turns`, `learner_profiles`):

```powershell
cd apps/web
npx.cmd vercel env run --environment production -- node ../../scripts/bootstrap-web-neon.mjs
```

Then `gh workflow run migrate-neon.yml` (may fail on stale `alembic_version`; bootstrap is enough for web critical path).

---

## Post-reset smoke (manual)

1. Hard refresh or sign out/in.
2. `/onboarding` → complete flow.
3. Tutor message → `/app/memory` → Refresh.
4. Lesson quiz → `/app/progress` → Refresh.
5. Coach session — physics-scoped drills if exam date set.

---

## Never

- Commit `DATABASE_URL`, `.database-url.local`, `Cron_Secret.txt`, or `.env.production.local`.
- Assume partial reset clears the plan UI — profile must be deleted for a true fresh start.
- Use `Set-Clipboard` with `vercel env run` on Windows (stdout is unreliable).

---

## Related

- `scripts/reset-learner.mjs` — CLI entry
- `scripts/check-learner-state.mjs` — row counts per learner
- `scripts/verify-neon-schema.mjs` — web table presence
- `scripts/bootstrap-web-neon.mjs` — idempotent web schema on Neon
- `skills/neon-direct-route/SKILL.md` — Neon access patterns
- `skills/onboarding-flow/SKILL.md` — what full reset restarts
