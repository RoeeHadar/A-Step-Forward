# Coordinator Roadmap — Phase 2

## P0 — User-visible improvements (run in parallel)

### I. Hebrew default + full RTL layout  (stream: `01-frontend`)

**Goal**: The website defaults to Hebrew (`he`). All UI text, navigation, labels, and page
layouts must be right-to-left. English is available via the language switcher.

**Acceptance**:
- `<html lang="he" dir="rtl">` by default.
- `tailwind.config` + CSS: RTL-aware utilities (`ml-*`→`ms-*`, `pl-*`→`ps-*`, etc.) OR use
  `@tailwindcss/rtl` or `logical` CSS properties. No hardcoded `left`/`right` margins.
- The locale switcher in `SiteHeader` sets `he` (default) / `en` and persists to
  `localStorage`.
- `apps/web/src/i18n/messages/he.ts` (or `.json`) contains all Hebrew translations for every
  key already in `apps/web/src/i18n/messages/en.ts`.
- The Clerk-rendered components (`<SignIn>`, `<SignUp>`, `<UserButton>`) have `locale="he-IL"`
  passed to `ClerkProvider`.
- Smoke: GET `/` → HTML contains `dir="rtl"` and `lang="he"`. GET `/sign-in` → 200.

**Key files to touch**:
- `apps/web/src/app/layout.tsx` — set `dir`/`lang` dynamically from user locale
- `apps/web/src/providers/app-providers.tsx` — pass `locale` to `ClerkProvider`
- `apps/web/src/providers/i18n-provider.tsx` + `config.ts` — default locale = `he`
- `apps/web/src/i18n/messages/he.ts` — add all Hebrew strings
- Tailwind: prefer CSS logical properties (`ps`, `pe`, `ms`, `me`, `bs`, `be`) everywhere

**Do NOT change**: route structure, auth flow, API calls.

---

### U. Visual polish pass  (stream: `01-frontend`)

**Goal**: The website looks professional, warm, and modern. Current state has basic shadcn
components but lacks personality.

**Acceptance**:
- Landing page (`/`) hero: compelling headline in Hebrew, sub-headline, CTA button ("התחל ללמוד"), 
  feature cards (Tutor, Mentor, Coach, Reviewer) with icons and descriptions.
- App dashboard (`/app`): cards have micro-animations (Framer Motion already installed), 
  progress bars are visually polished.
- Typography: set a good Google Font (Heebo for Hebrew, Inter/DM Sans for English fallback)
  via `next/font`. Hebrew requires a font with Hebrew glyph support.
- Color theme: a warm blue + amber accent (already in globals.css? if not, set it).
- Mobile responsive: check at 375px, 768px, 1280px.
- No broken layouts on RTL (coordinate with stream I).

**Key files**:
- `apps/web/src/app/globals.css`
- `apps/web/src/components/landing-hero.tsx`
- `apps/web/src/app/page.tsx`
- `apps/web/src/app/(app)/app/page.tsx`

---

### C. Chat hiccup fix  (stream: `01-frontend` + `02-backend-api`)

**Goal**: Opening a chat session is smooth with no visible flash/error on first load.

**Current symptom** (reported by user): a "hiccup" when starting a chat. This is likely:
1. The Render backend spins down (free tier cold start → first request takes 5–15s)
2. OR the frontend `/app/chat/[agent]` page crashes on mount before the user sends a message
3. OR a CORS error for the first request

**Acceptance**:
- `/app/chat/[agent]` loads without error or visible crash.
- Sending the first message shows a clear loading state (spinner or "Thinking…" indicator).
- If the backend is cold-starting, a friendly "Connecting to your AI tutor, please wait…"
  message is shown for up to 15s, then retries once.
- CORS headers are correct: `Access-Control-Allow-Origin` includes the Vercel URL.

**Investigation checklist** (sub-agent must check these before coding):
1. GET `https://a-step-forward-waij.vercel.app/app/chat/tutor` — check browser console
2. Check `apps/web/src/app/(app)/app/chat/[agent]/page.tsx` for any uncaught async errors
3. Check `apps/api/app/routers/chat.py` for CORS + streaming headers

---

## P1 — Content database (stream: `07-curriculum` + `05-graphrag`)

### K. Research ingest for STEM curriculum

**Goal**: Scrape/collect high-quality public-domain or CC-licensed educational content for:
- **Mathematics**: arithmetic, fractions, algebra, geometry, number theory
- **Calculus**: limits, derivatives, integrals, series
- **Linear Algebra**: vectors, matrices, eigenvalues, transformations
- **Statistics & Probability**: distributions, hypothesis testing, Bayesian inference
- **Physics**: mechanics, electromagnetism (basics)

**Sources** (free, legal, high quality):
- OpenStax textbooks (https://openstax.org — CC BY 4.0): `precalculus-2e`, `calculus-vol-1`,
  `calculus-vol-2`, `linear-algebra`, `introductory-statistics`, `university-physics-vol-1`
- Paul's Online Math Notes (https://tutorial.math.lamar.edu — free educational use):
  Calculus I/II/III notes
- Wikipedia math articles for concept definitions

**Approach**:
1. Write a Python script `scripts/ingest_content.py` that:
   - Downloads OpenStax book HTML (they have a public API: `https://openstax.org/apps/archive/...`)
   - Parses chapters into `Lesson` objects matching `packages/schemas/src/curriculum.ts`
   - Chunks into ≤1000-token segments
   - Inserts into `kg_chunks` table (Neon) with subject tag
   - Also inserts into `curriculum.lessons` if a full lesson structure is available
2. Run the script against at least 3 OpenStax books (precalculus, calculus-vol-1, statistics)
3. Verify with `SELECT COUNT(*), subject FROM kg_chunks GROUP BY subject;` against Neon
4. Update `apps/web/src/lib/seed-lessons.generated.json` with a sample of new lesson objects

**Constraints**:
- Do NOT use paid embedding APIs. Use `sentence-transformers/all-MiniLM-L6-v2` (384-dim,
  free, fast) OR the existing HuggingFace inference API (no key needed for public models).
- Embeddings go in `kg_chunks.embedding` (vector column exists).
- Mark every chunk with `source_url`, `license = "CC BY 4.0"`, `subject` metadata.
- The script must be idempotent (re-runnable without duplicates — upsert on `source_url+chunk_idx`).

---

## P2 — Deferred to phase 3

- Custom domain `astepforward.app`
- Clerk production instance (needs domain)
- Key rotation (Groq + Clerk dev keys)
- Marketing posts (HN, Product Hunt, LinkedIn)
- Demo GIF recording

---

## Coordinator dispatch plan

**Session 6** (this session): dispatch streams I + U + C in parallel (3 sub-agents).
Wait for all to land, smoke test, then dispatch K (content ingest) separately.

**Parallel-safe**: I, U, C touch different files (I18n config, landing page UI, chat page/API).
**Not parallel with I**: K touches `seed-lessons.generated.json` — wait for I to finish first
to avoid RTL-related string conflicts.

### Sub-agent prompts summary

**Agent A (I18N + RTL)**:
Read PLAN.md + `.cursor/subagent-briefs/01-frontend.md` + this ROADMAP §I, then:
implement Hebrew default with RTL layout per spec.

**Agent B (Visual Polish)**:
Read PLAN.md + `.cursor/subagent-briefs/01-frontend.md` + this ROADMAP §U, then:
implement visual polish per spec.

**Agent C (Chat Hiccup)**:
Read PLAN.md + `.cursor/subagent-briefs/01-frontend.md` + `.cursor/subagent-briefs/02-backend-api.md` + this ROADMAP §C, then:
investigate and fix the chat cold-start hiccup.

**Agent K (Content Ingest)**:
Read PLAN.md + `.cursor/subagent-briefs/07-curriculum.md` + `.cursor/subagent-briefs/05-graphrag.md` + this ROADMAP §K, then:
implement the content scraping and ingest script.
