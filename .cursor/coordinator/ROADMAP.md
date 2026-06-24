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

## P2 — Phase 3 (current focus)

### E. Real agent routing with Groq  (stream: `03-agents`)

**Goal**: End-to-end Groq-backed chat. Currently `/v1/chat` may return stub responses.
The Orchestrator/Router agent must receive the user message, route it to the correct
learner-facing agent (Tutor, Mentor, Coach, etc.), call Groq, and stream the reply.

**Acceptance**:
- POST `https://asf-api-q566.onrender.com/v1/chat` with `{"agent": "tutor", "message": "What is a derivative?", "learner_id": "test-123"}` → streams a real Groq response (not a stub).
- The response correctly identifies itself as a Socratic tutor, not a generic assistant.
- Latency first-token < 4s on Render free tier (warm).

**Key files**:
- `packages/agents/agents/learner_facing/tutor/` — Tutor agent implementation
- `packages/agents/agents/system/orchestrator/` — router
- `apps/api/app/routers/chat.py` — streaming endpoint
- `packages/agents/agents/base/llm.py` — Groq client (already implemented)
- `prompts/tutor/` — tutor prompt

Read `.cursor/subagent-briefs/03-agents.md` before starting.

---

### F. Assessment Generator + Grader stubs  (stream: `03-agents`)

**Goal**: A learner can request a quiz on a topic; the Assessment Generator creates 3–5
questions; the Grader evaluates answers. These can be stub implementations (returning
hardcoded structure) as long as the API contract and agent classes are wired up.

**Acceptance**:
- `GET /v1/assessment?topic=derivatives&level=beginner` returns a JSON array of 3–5 questions.
- `POST /v1/grade` with `{question, answer}` returns `{correct: bool, feedback: string}`.
- Both endpoints documented in `apps/api/README.md`.

---

### G. ADRs (Architecture Decision Records)

**Goal**: Record the key architecture decisions made during Phase 0–2.

**Acceptance**:
- `docs/adr/001-hosting.md` — Vercel + Render over Fly.io (credit card constraint)
- `docs/adr/002-llm.md` — Groq Cloud free tier over Anthropic/OpenAI
- `docs/adr/003-auth.md` — Clerk dev keys, no prod instance until custom domain
- `docs/adr/004-database.md` — Neon + Upstash + Neo4j AuraDB
- Each ADR follows the Markdown ADR template: Status, Context, Decision, Consequences.

---

### H. Demo screenshot  (carry-over from session 7 D4)

Screenshoot `https://a-step-forward-waij.vercel.app/` (landing) and `/sign-in`.
Save to `docs/screenshots/landing.png` and `docs/screenshots/sign-in.png`.
Update README hero image reference. Use `browser-use` subagent or `cursor-ide-browser` MCP.

---

## P2.5 — User-reported issues (Phase 3 hotfix batch, session 10)

### V. Dark visual redesign — Higgsfield-style  (stream: `01-frontend`)

**User request**: "The design lacks. I suggest using HiggsField for it."
Higgsfield.ai uses a distinctive dark AI-product aesthetic. Apply it site-wide.

**Exact design spec**:
- **Background**: `#0f1113` (near-black) in dark mode. Keep light mode reasonable but make dark mode the visual identity.
- **Accent colour**: `#d1fe17` (electric chartreuse / neon lime). Apply to exactly ONE focal element per section: primary CTA button, active nav item, logo dot.
- **Typography**: Add `Space Grotesk` (Google Font, weights 600+700) for all headings (`h1`–`h4`). All headings: `text-transform: uppercase`, `letter-spacing: 0.04em`. Body stays with Inter/Heebo.
- **Cards**: `border-radius: 12px`, surface `rgb(26, 28, 30)`, 1px border `rgba(255,255,255,0.07)`. Subtle glassmorphism via `backdrop-filter: blur(8px)`.
- **Badges / pills**: fully rounded, `rgba(209,254,23,0.1)` fill, chartreuse text.
- **Buttons**: primary = chartreuse bg + dark text. Focus ring = chartreuse glow, NOT a border.
- **Footer**: invert — chartreuse/lime background, dark text. (Landing page footer only.)
- **Breakpoints**: no change to existing responsive setup.

**Files to touch**:
- `apps/web/src/app/globals.css` — update CSS custom properties for dark theme, add Space Grotesk import.
- `apps/web/src/components/landing-hero.tsx` — apply new heading style, chartreuse CTA, glassmorphism cards.
- `apps/web/src/app/(app)/app/page.tsx` — dashboard cards use new surface style.
- `apps/web/src/components/site-header.tsx` — logo dot or brand name accent in chartreuse.
- Do NOT break RTL layout. Do NOT remove i18n wiring.

**Acceptance**:
- `pnpm --filter @asf/web build` passes.
- In dark mode, background is `#0f1113` or very close, CTA button is chartreuse, cards have subtle glass border.
- In light mode, the design is still professional (can keep existing light theme or do a warm white).

---

### L. Fix Hebrew content on landing page  (stream: `01-frontend`)

**User report**: "When switching to Hebrew the main screen shows the screen itself in English. Only the options to the right are in Hebrew."

**Root cause (diagnosed by manager)**:
The `I18nProvider` in `apps/web/src/providers/i18n-provider.tsx` reads `localStorage['asf-locale']` in a `useEffect`. If the user's browser has `'en'` stored from a previous session (before Hebrew was the default), the `useEffect` overrides the server-supplied `initialLocale='he'` and switches the content to English. The nav (`SiteHeader`) and landing hero (`LandingHero`) both use `useI18n()` so they should both update when `setLocale('he')` is called — but if the initial `useEffect` restores 'en' AFTER the initial render, the user sees English.

**Fix**:
1. Bump the storage key from `'asf-locale'` to `'asf-locale-v2'` in `apps/web/src/i18n/locale-storage.ts`. Any user with the old key stored as `'en'` will not have the new key and will correctly get the default `'he'`.
2. In `apps/web/src/providers/i18n-provider.tsx`, change every reference to `LOCALE_STORAGE_KEY` to use the new key (they're imported from `locale-storage.ts` so this is automatic once you change the constant).
3. Also fix these hardcoded English strings that bypass i18n:
   - `apps/web/src/components/agent-chat.tsx` line ~99: `"Ask {agentDisplayNames[agentName]} anything about your current lesson."` → add to `messages.he` + `messages.en` as `chat.placeholder` and use `t.chat?.placeholder ?? '...'`.
   - `apps/web/src/components/agent-chat.tsx` line ~83: `statusMessage` — `'Thinking…'` is English, `'מתחבר לשרת…'` is Hebrew. Use the i18n system or at minimum make both messages conditionally come from the locale.
4. Add to `apps/web/src/i18n/messages.ts` under both `en` and `he`:
   ```ts
   chat: {
     placeholder: 'Type your message…' / 'הקלד את הודעתך…',
     thinking: 'Thinking…' / 'חושב…',
     connecting: 'Connecting to AI server…' / 'מתחבר לשרת ה-AI…',
     empty: 'Ask {agent} anything.' / 'שאל את {agent} כל שאלה.',
   }
   ```

**Acceptance**:
- First-time user (no localStorage) sees Hebrew landing page with all content in Hebrew.
- User with old `'en'` localStorage also now sees Hebrew (old key is ignored).
- Language switcher still works: switching to English shows English content everywhere.

---

### C2. Chat cold-start warm-up  (stream: `01-frontend` + `02-backend-api`)

**User report**: "The chat still hits a hiccup when attempting to send a message."

**Root cause (diagnosed by manager)**:
The Render free tier backend sleeps after ~5 minutes of inactivity. The first chat request hits a cold start of 10–20s, which causes the 15s timeout in `apps/web/src/app/api/chat/route.ts` to fire. The backend returns a 502 or times out, and the frontend shows the mock/fallback response. The auto-retry waits only 500ms — not enough for a cold start.

**Fix**:
1. **Backend warm-up endpoint**: `apps/api/app/routers/chat.py` or `main.py` — add `GET /v1/warmup` that returns `{"status": "warm"}` immediately (no DB or LLM call). This wakes up Render before the user's first message.
2. **Frontend warm-up**: In `apps/web/src/app/(app)/app/chat/[agent]/page.tsx` (server component), add a `fetch(${API_BASE_URL}/v1/warmup, { signal: AbortSignal.timeout(3000) }).catch(() => {})` call during server-side render. This fires the warm-up the moment the user navigates to the chat page, NOT when they send a message. Render starts waking up ~10s before the first message.
3. **Client warm-up ping**: In `apps/web/src/components/agent-chat.tsx`, add a `useEffect` that fires a `fetch('/api/warmup')` immediately on mount. Add `apps/web/src/app/api/warmup/route.ts` that proxies to `${API_BASE_URL}/v1/warmup` with a 5s timeout and silently ignores errors.
4. **Retry with backoff**: In `apps/web/src/app/api/chat/route.ts`, increase `BACKEND_FETCH_TIMEOUT_MS` from 15000 to 25000. Between the two attempts, add a 3-second delay (`await new Promise(r => setTimeout(r, 3000))`).
5. **UX**: In `agent-chat.tsx`, show "מחמם את שרת ה-AI…" (Hebrew) / "Warming up AI server, this takes ~15s on first load…" (English) immediately when `isLoading` and `userMessageCountRef.current === 1` (i.e., first message).

**Acceptance**:
- When chat page loads, a warm-up request fires silently in the background.
- First user message: if warm-up succeeded, response arrives within 3–5s. If Render was cold, the extended 25s timeout + warm-up message keeps the user informed.
- No "hiccup" (error flash / mock response) on the first send.

---

### K2. Curriculum categories — 13 subject areas with sub-sections  (stream: `07-curriculum`)

**User request**: Lectures must be divided into 13 categories, each with sub-sections.

**Categories** (use these exact Hebrew names):
1. `math-hs-3` — מתמטיקה לתיכון 3 יחידות
2. `math-hs-4` — מתמטיקה לתיכון 4 יחידות
3. `math-hs-5` — מתמטיקה לתיכון 5 יחידות
4. `math-middle` — מתמטיקה לחטיבת ביניים
5. `calculus` — חשבון דיפרנציאלי ואינטגרלי
6. `pre-calculus` — קדם-חשבון
7. `linear-algebra` — אלגברה לינארית
8. `statistics` — סטטיסטיקה והסתברות
9. `physics-hs` — פיזיקה לתיכון
10. `physics-middle` — פיזיקה לחטיבת ביניים
11. `physics-pre-uni` — קדם-פיזיקה לאוניברסיטה
12. `physics-1` — פיזיקה 1
13. `physics-2` — פיזיקה 2

**Sub-sections per category** (create a minimum of 4 sub-sections per category):
- `math-hs-5`: algebra-and-functions, trigonometry, analytic-geometry, calculus-hs, probability-hs
- `math-hs-4`: algebra-and-functions, geometry, trigonometry-basic, probability-basics
- `math-hs-3`: arithmetic-and-algebra, geometry-basic, statistics-basic, linear-equations
- `math-middle`: numbers-and-operations, fractions-and-decimals, ratios, intro-algebra, geometry-middle
- `calculus`: limits, derivatives, integrals, series-and-sequences, multivariable-intro
- `pre-calculus`: functions-and-graphs, polynomial-functions, trigonometry-full, exponentials-and-logs
- `linear-algebra`: vectors, matrices-and-systems, determinants, eigenvalues, linear-transformations
- `statistics`: descriptive-statistics, probability-theory, distributions, hypothesis-testing, bayesian-inference
- `physics-hs`: mechanics, waves-and-optics, electricity, modern-physics
- `physics-middle`: forces-and-motion, energy-and-work, waves, light-and-sound
- `physics-pre-uni`: kinematics, newton-laws, energy-conservation, thermodynamics-intro
- `physics-1`: kinematics-advanced, newton-laws-advanced, work-energy-theorem, rotation, fluids
- `physics-2`: electrostatics, current-circuits, magnetic-fields, electromagnetic-induction, optics-advanced

**Implementation**:
1. Create `apps/web/src/lib/curriculum-categories.ts` — export the 13 categories as a typed structure:
   ```ts
   export interface CurriculumSection { id: string; heLabel: string; enLabel: string; }
   export interface CurriculumCategory { id: string; heLabel: string; enLabel: string; sections: CurriculumSection[]; }
   export const CURRICULUM_CATEGORIES: CurriculumCategory[] = [...];
   ```
2. Create `apps/web/src/app/(app)/app/lessons/page.tsx` (or update if exists) — shows all 13 categories as a browsable grid. Each category card shows the Hebrew name, section count, and links to `lessons/[category]`.
3. Create `apps/web/src/app/(app)/app/lessons/[category]/page.tsx` — shows sub-sections for a category. Each sub-section links to `lessons/[category]/[section]`.
4. Create a stub `apps/web/src/app/(app)/app/lessons/[category]/[section]/page.tsx` — shows lesson list (empty state with "Coming soon" / "בקרוב" if no lessons loaded).
5. Update `apps/web/src/components/site-header.tsx` or app sidebar to link to `/app/lessons` as the "Lessons" nav item.
6. Add English labels to `messages.en.nav.lessons` and Hebrew to `messages.he.nav.lessons` (already exist — just ensure the link works).

**Do NOT touch** the API or Alembic — this is purely a frontend data/routing change for now.

**Acceptance**:
- `pnpm --filter @asf/web build` passes.
- `/app/lessons` shows a grid of 13 category cards in Hebrew.
- `/app/lessons/calculus` shows 5 sub-section cards.
- No TypeScript errors.

---

## P3 — Deferred to phase 4

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
