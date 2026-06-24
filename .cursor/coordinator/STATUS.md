# A Step Forward — Coordinator Status

Last updated: 2026-06-24T18:31:00Z by Manager check-in (pre-session 7)

## Launch status: **LIVE** — Phase-2 complete; CI stabilised; Phase-3 queued

---

## Acceptance checklist

- [x] `apps/web` deployed — https://a-step-forward-waij.vercel.app
- [x] `/` returns 200
- [x] `/sign-in` returns 200
- [x] `/api/health` returns 200
- [x] Render backend live — https://asf-api-q566.onrender.com
- [x] `/healthz` 200, `/readyz` 200
- [x] Clerk auth working
- [>] Hebrew default + RTL layout — code is on main (`e016402`); Vercel native integration redeploys automatically; verify `lang="he" dir="rtl"` on `/` in a browser after next successful build
- [x] Visual polish pass — hero Hebrew headline, agent feature cards, MotionCard dashboard, Heebo + warm blue/amber theme
- [x] Chat hiccup fixed — skeleton loader, error boundary, "מתחבר לשרת…" after 3s, auto-retry, backend fetch timeout
- [x] Content DB seeded — `scripts/ingest_content.py` on main (`2534321`); run manually against Neon with DATABASE_URL
- [>] CI green — Lint & Test was failing (Ruff errors in ingest_content.py); **fixed by manager** (`0455678`); Deploy Web CI action failing with "You do not have access to the specified account" (VERCEL_ORG_ID secret wrong) — Vercel native deploy still works; fix this in session 7
- [ ] Polished README, SECURITY.md, ADRs
- [ ] Demo screenshot / GIF

---

## Manager actions taken before session 7

1. **`41d2795`** — Fixed `apps/web/src/app/layout.tsx` invalid UTF-8 byte (0xB7 middle-dot) that was crashing webpack and blocking all Vercel builds since `e016402`.
2. **`d67d78a`** — Added `.github/workflows/dependabot-lockfile.yml` (auto-regenerates pnpm-lock.yaml on Dependabot PRs), `.editorconfig` (enforces UTF-8 for all source files), `skills/pnpm-lockfile-ci/SKILL.md` (documents diagnosis + fix for recurring lockfile and encoding issues).
3. **`0455678`** — Fixed 2 Ruff lint errors in `scripts/ingest_content.py` (RUF005, UP017) that were breaking Lint & Test CI on every commit.
4. Closed 5 stale Dependabot npm PRs (#10–14) that had frozen lockfiles; they'll be recreated correctly now that the lockfile workflow is in place.

---

## Session 7 directives (from manager)

### Priority order

**D1 (HIGH) — Fix Vercel deploy CI action**
The `.github/workflows/deploy-web.yml` is failing with "You do not have access to the specified account" because `VERCEL_ORG_ID` stored in GitHub Actions secrets does not match the token's scope. Options:
- Retrieve the correct `VERCEL_ORG_ID` from the Vercel project settings and update the GitHub secret, OR
- Simplify the workflow: rely entirely on Vercel's native GitHub integration (which works fine) and remove the manual CLI deploy step from `deploy-web.yml` to eliminate the spurious failure.
**Preferred approach**: simplify the workflow — remove the manual `vercel deploy` CLI step; keep only the `pnpm build` smoke check in CI to confirm the app compiles, and let Vercel's GitHub App handle actual deployment.

**D2 (HIGH) — RTL smoke verification**
After D1 fixes CI:
- GET `https://a-step-forward-waij.vercel.app/` and confirm the HTML response contains `lang="he"` and `dir="rtl"`.
- If not present, investigate why `getServerLocale()` is returning `en` instead of `he` and fix.
- Document result in STATUS.md.

**D3 (MEDIUM) — Docs + README polish**
The end-state acceptance list requires a polished README. The current README is sparse. Sub-agent should:
- Update `README.md` at repo root: add badges (Vercel deploy status, CI status), a description in both English and Hebrew, setup instructions (local dev, environment variables), and a link to the live site.
- Create `SECURITY.md` (responsible disclosure policy, pointing to GitHub security advisories).
- Verify `LICENSE` (MIT) exists and is dated correctly.

**D4 (LOW) — Demo screenshot**
Take a screenshot of the live site (landing page + dashboard + chat page) and commit to `docs/screenshots/`. Update README to reference it. This can be done with the browser MCP tool.

**D5 (ONGOING) — CI watch**
After every push to main, verify Lint & Test goes green. If any new Ruff or TypeScript errors appear, fix them immediately before moving to the next stream. Use `skills/pnpm-lockfile-ci/SKILL.md` for lockfile issues.

---

## Next session priorities

1. D1 — Fix Vercel deploy CI workflow (remove broken CLI step, keep pnpm build smoke)
2. D2 — RTL smoke: confirm `lang="he" dir="rtl"` on live `/`
3. D3 — README + SECURITY.md polish

---

## Hands-off until manager check-in

true — deliver D1+D2+D3 then report back.
