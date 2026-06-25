# Coordinator Directive — Round 3 (2026-06-25)

> This is the master directive from the project supervisor. Read it completely before taking
> any action. Execute every task below. Never ask the user a question.

---

## Context snapshot

- **Live URLs**: Frontend → `https://a-step-forward-waij.vercel.app` | Backend → `https://asf-api-q566.onrender.com`
- **Repo**: `RoeeHadar/A-Step-Forward` (public, MIT)
- **Active branch**: `main` (clean, 1 untracked entry now in `.gitignore`)
- **In-flight branches** (need assessment and likely merge/archive):
  `chore/infra/workspace-stabilization`, `feat/agents/03-phase3-system-agents`,
  `feat/curriculum/openstax-ingest`, `feat/frontend/chat-cold-start-fix`,
  `feat/frontend/hebrew-rtl-default`, `feat/frontend/visual-polish`,
  `feat/mcp/05-server-improvements`, `release/phase-1-integration`

---

## Priorities (strict order)

### P0 — Fix chat (users can sign up but AI is unreachable)

**Symptom**: After sign-up, the chat page loads but the AI agent returns only the mock
fallback (`"That's a great question… what do you already know…"`). The real Groq
LLM is not responding.

**Root cause diagnosis** (do this first):
1. Hit `https://asf-api-q566.onrender.com/healthz` and `/readyz` — record the response time.
   If it takes > 20 seconds, the Render free tier is sleeping and the 25s frontend
   timeout is firing before the backend wakes up.
2. Check the Render service logs (look at `.github/workflows/` or any available log
   surface). If the backend returns a 500 with `groq` in the stack trace, the Groq
   key is the issue (but the user does not want to rotate it yet — see fallback plan).
3. Check CORS: try `curl -I -X OPTIONS https://asf-api-q566.onrender.com/v1/chat`
   with an `Origin: https://a-step-forward-waij.vercel.app` header.

**Fixes to implement (do all three — they stack)**:

**Fix A — Extend cold-start grace window**
In `apps/web/src/app/api/chat/route.ts`: increase `BACKEND_FETCH_TIMEOUT_MS` to
`55_000` (55 seconds). Render free tier takes up to 50s to wake.
Add a pre-warm call: at the top of `POST`, fire-and-forget a GET to
`${API_BASE_URL}/v1/warmup` immediately (don't await), then wait 2 seconds before
the first real chat POST to let the backend wake.

```typescript
// fire-and-forget warm-up so Render wakes before the real request
fetch(`${API_BASE_URL}/v1/warmup`).catch(() => {});
await new Promise((r) => setTimeout(r, 2000));
```

**Fix B — Better "waking up" UX**
In `apps/web/src/components/agent-chat.tsx`: when `isLoading` is true and more than
3 seconds have elapsed with no tokens received yet, show a warm-up banner:
```
🔄 Waking the AI up… (free hosting — first response takes up to 30s)
```
Hide the banner as soon as the first token arrives.

**Fix C — Groq key fallback**
If Groq key is confirmed missing/invalid: add an environment-variable-controlled
fallback in `packages/agents/agents/base/llm.py` that uses **OpenAI-compatible
Anthropic** (model `claude-haiku-4-5`, env `ANTHROPIC_API_KEY`). The API is
OpenAI-compatible so the same client works with just a `base_url` swap. Document
this fallback in `docs/adr/0006-llm-fallback.md`.
**Only implement Fix C if diagnosis confirms the Groq key is the issue.**

Ship as one small PR: `fix(chat): extend cold-start timeout + wakeup UX`.

---

### P1 — Content pipeline: Learning Database → website

The user maintains a local folder called `Learning Database/` (now `.gitignore`d).
It contains **76 Hebrew PDF files** across 15 subject directories. This folder is
the authoritative source for the FREE TIER content of the website.

**Structure of the Learning Database** (surveyed 2026-06-25):

```
Learning Database/
├── Calculus 1/                          (7 PDFs — university assignments + solutions)
├── Linear Algebra/
├── Statistics & Probability/
├── Math Pre-University/
├── Middle School Math - 7th grade/
├── Middle School Math - 8th grade/
├── Middle School Math - 9th grade/
├── High School Math - 3 points/
│   ├── Bagrut Tests/                    ← DRAG-AND-DROP PDF viewer
│   ├── High School Math - 10th grade 3 points/   (801_gool.pdf, 802_gool.pdf)
│   └── High School Math - 11th grade 3 points/   (803_gool.pdf)
├── High School Math - 4 points/
│   ├── Bagrut Tests 11th grade/         ← DRAG-AND-DROP
│   ├── Bagrut Tests 12th grade/         ← DRAG-AND-DROP
│   ├── High School Math - 10th grade 4 points/   (804_gool.pdf)
│   ├── High School Math - 11th grade 4 points/   (804_gool.pdf)
│   └── High School Math - 12th grade 4 points/   (805_gool.pdf)
├── High School Math - 5 points/
│   ├── Bagrut Tests 11th grade/         ← DRAG-AND-DROP
│   ├── Bagrut Tests 12th grade/         ← DRAG-AND-DROP
│   ├── High School Math - 10th grade 5 points/   (806_gool.pdf)
│   ├── High School Math - 11th grade 5 points/   (806_gool.pdf)
│   └── High School Math - 12th grade 5 points/   (807_gool.pdf)
├── Physics High School/
│   ├── Bagrut Electricity & Magneticism/ ← DRAG-AND-DROP (3 PDFs)
│   ├── Bagrut Labs/                      ← DRAG-AND-DROP (4 PDFs)
│   ├── Bagrut Mechanics/                 ← DRAG-AND-DROP (4 PDFs)
│   ├── Bagrut Optics & Matter/           ← DRAG-AND-DROP (4 PDFs)
│   ├── Physics 10th grade/               (7 PDFs)
│   ├── Physics 11th grade/               (7 PDFs)
│   └── Physics 12th grade/               (2 PDFs)
├── Physics Middle School/
├── Physics Pre-University/              (13 PDFs)
├── Physics 1/                           (13 PDFs — university)
└── Physics 2/                           (2 PDFs — university)
```

**Design rules** (from the user):

1. **Bagrut folders** → served as-is with a PDF viewer. No parsing, no AI splitting.
   Each Bagrut PDF renders in an embedded PDF viewer on a dedicated "Bagrut Exams"
   sub-page inside the subject.
2. **All other PDFs** → parsed, split by chapter/topic, stored as structured
   `content_section` records in Postgres, and rendered as rich text/LaTeX pages.
   A single PDF file (e.g., `806_gool.pdf`) may contain many chapters — each chapter
   becomes a separate navigable section on the website.
3. **Content grows over time**. The pipeline must be re-runnable (idempotent by
   `(subject_slug, source_file, chunk_index)`). When the user adds more PDFs to
   `Learning Database/`, running `make ingest` processes only the new/changed ones.
4. **Free tier**: all content browsable without login (or with a free account). No
   paywall on content.
5. **Premium tier**: agent-based tutoring (chat with Tutor, Coach, etc.). No payment
   integration yet — the tier exists structurally but is free.

**Sub-tasks (implement in this order)**:

#### ST-1: Database schema — `content_sections` + `bagrut_exams`

Migration file: `infra/alembic/versions/0008_content_sections.py`

```sql
-- content_sections: parsed content from textbooks
CREATE TABLE content_sections (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject       TEXT NOT NULL,          -- e.g. "high_school_math_5_points"
  grade         TEXT,                   -- e.g. "10th", "11th", "university"
  source_file   TEXT NOT NULL,          -- original filename
  chunk_index   INT  NOT NULL,          -- order within source file
  title         TEXT NOT NULL,          -- extracted chapter/section title (Hebrew)
  title_en      TEXT,                   -- English translation (optional)
  body_md       TEXT NOT NULL,          -- Markdown + KaTeX content
  body_html     TEXT,                   -- pre-rendered HTML (optional cache)
  page_start    INT,                    -- PDF page range
  page_end      INT,
  tier          TEXT NOT NULL DEFAULT 'free',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (subject, source_file, chunk_index)
);

-- bagrut_exams: served as raw PDFs
CREATE TABLE bagrut_exams (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject       TEXT NOT NULL,
  exam_type     TEXT NOT NULL,   -- e.g. "mechanics", "11th_grade", "labs"
  year          INT,
  source_file   TEXT NOT NULL,
  display_name  TEXT NOT NULL,
  file_url      TEXT NOT NULL,   -- Cloudflare R2 / public storage URL
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (subject, source_file)
);
```

#### ST-2: PDF ingestion script — `scripts/ingest_learning_db.py`

```
python scripts/ingest_learning_db.py --db-url $DATABASE_URL \
  --source "Learning Database/" \
  --storage-bucket $R2_BUCKET_NAME
```

Steps:
1. Walk the `Learning Database/` directory tree.
2. **Bagrut detection**: if the path contains `Bagrut`, upload the PDF to R2
   (or a public Postgres `bytea` column as a fallback if R2 is not configured),
   upsert a `bagrut_exams` row, skip parsing.
3. **Content PDFs**: use `pdfplumber` (primary) or `PyMuPDF` (fallback) to extract
   text. Handle Hebrew RTL text correctly. Split into chapters by detecting
   level-1/2 headings (regex on Hebrew chapter markers like `פרק`, `יחידה`, etc.,
   or font-size changes via pdfplumber).
4. Convert each chapter to Markdown (preserve math expressions as `$...$` / `$$...$$`
   using `latex2sympy` or regex heuristics for common patterns).
5. Upsert into `content_sections` (idempotent).
6. Log skipped/failed files with reasons; never crash on a single bad PDF.

Add to `Makefile`:
```makefile
ingest:
	python scripts/ingest_learning_db.py --db-url $(DATABASE_URL) \
	  --source "Learning Database/" --storage-bucket $(R2_BUCKET)
```

#### ST-3: Content browsing API routes

Add to `apps/api/app/routers/content.py`:

- `GET /v1/subjects` — list all subjects with section counts.
- `GET /v1/subjects/{subject}/sections` — list sections (title, chunk_index, grade).
- `GET /v1/subjects/{subject}/sections/{chunk_index}` — full Markdown body.
- `GET /v1/subjects/{subject}/bagrut` — list Bagrut exam records (display_name, year, file_url).

No auth required (free tier). Add to `apps/api/app/main.py`.

#### ST-4: Frontend content browser

New routes under `apps/web/src/app/(app)/app/learn/`:

```
/learn                         → Subject grid (cards per subject)
/learn/[subject]               → Section list for the subject
/learn/[subject]/[chunkIndex]  → Lesson reader (Markdown + KaTeX)
/learn/[subject]/bagrut        → Bagrut exam list + embedded PDF viewer
```

Design:
- Subject grid: card per subject (icon + name + section count badge).
- Section list: sortable by grade/chapter, search box.
- Lesson reader: `react-markdown` + `remark-math` + `rehype-katex` for LaTeX;
  prev/next navigation; "Chat with Tutor about this" button linking to
  `/app/chat/tutor?context=<section_id>` (premium CTA).
- Bagrut page: list of exams with year + topic chip; clicking opens the PDF in an
  embedded `<iframe>` or `react-pdf` viewer.

Update the app sidebar to include "Learn" with a book icon.

#### ST-5: Content management for new uploads

In `scripts/ingest_learning_db.py`, add a `--watch` flag that uses `watchdog`
to monitor `Learning Database/` for new/changed files and re-ingests automatically.
Document in `docs/infra/local-dev.md`.

Also add a simple `GET /v1/admin/content/status` route (admin-only) showing
total sections, last ingest timestamp, and any failed files.

---

### P2 — Private lesson booking page

New page: `apps/web/src/app/book/page.tsx`

**URL**: `/book` (link in main nav header + landing page hero CTA button)

**Section 1 — About the tutor**

```tsx
<section className="about">
  <div className="avatar-placeholder">
    {/* placeholder box with text "Photo coming soon" */}
  </div>
  <div>
    <h2>Roee Hadar — Math & Physics Tutor</h2>
    <p>
      {/* Short Hebrew + English bio — use placeholder copy for now */}
      מורה מנוסה למתמטיקה ופיזיקה לכל הרמות — מחטיבת הביניים ועד ה-12, 
      כולל הכנה לבגרות, קורסים אקדמיים, ופיזיקה אוניברסיטאית. 
      שיעורים מותאמים אישית, בקצב שלך.
    </p>
    <p className="en-bio">
      Experienced Math &amp; Physics tutor for all levels — middle school through grade 12,
      Bagrut prep, and university courses. Personalised sessions at your pace.
    </p>
  </div>
</section>
```

**Section 2 — Booking form**

Fields:
- Full name (text)
- Email address (email)
- Phone number (tel, optional)
- Preferred date (date picker — show a calendar; no backend availability system yet,
  any date is selectable)
- Preferred time (time picker, 08:00–20:00 in 30-min increments)
- Session duration: radio/slider — **1 hour / 1.5 hours / 2 hours / 2.5 hours / 3 hours**
- Subject (dropdown: Math, Physics, Other)
- Notes (textarea, optional)
- **Price preview** (calculated live):
  ```
  150 ₪ × {hours} = {total} ₪
  ```
  Show "Payment is handled at the start of the session."

On submit: `POST /api/book` (Next.js route handler) → sends an email to the tutor
via **Resend** (free tier, `resend.com`) using `RESEND_API_KEY` env var. If
`RESEND_API_KEY` is not set, log the booking to Postgres `bookings` table only.

Add `bookings` table in a new migration `0009_bookings.py`:
```sql
CREATE TABLE bookings (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  email       TEXT NOT NULL,
  phone       TEXT,
  date        DATE NOT NULL,
  time        TIME NOT NULL,
  duration_h  NUMERIC(3,1) NOT NULL,   -- 1.0, 1.5, 2.0, 2.5, 3.0
  subject     TEXT NOT NULL,
  notes       TEXT,
  price_ils   INT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'pending',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**Design**: match the site's dark glassmorphism style. Price preview is a bold
accent-colored callout. "Book a Lesson" CTA button in the main header.

Add `RESEND_API_KEY` to `render.yaml` (sync: false) and `.env.example`.

---

### P3 — Free vs Premium tier structure

- **Free tier**: all `/learn/` content, Bagrut exams. No login required.
- **Premium tier**: `/app/chat/*`, `/app/memory`, `/app/progress`. Requires login.
  No payment gate for now — just Clerk auth.
- Add a visual indicator in the UI: a small "✨ Premium" badge on agent chat pages.
  A tooltip: "Currently free for all users — subscription coming soon."
- In the main subject page, add a "Chat with the Tutor about this" card/section
  marked as Premium (but immediately accessible).

---

### P4 — In-flight branch triage

Assess each in-flight branch against current `main` (most are behind main after
recent direct commits). For each:

1. `git log main..<branch> --oneline` — how many commits ahead?
2. If the branch adds real new value not on `main` → rebase + PR.
3. If the branch is effectively merged or fully superseded by `main` → delete the
   remote branch with a note in `docs/sprint.md`.

Specific branches to handle:
- `feat/agents/03-phase3-system-agents` → check if research/kg_builder agents are
  materially better than what's on main. If yes, PR it.
- `feat/curriculum/openstax-ingest` → superseded by the new content pipeline (P1).
  Archive and note.
- `feat/mcp/05-server-improvements` → merge or cherry-pick improvements onto main.
- `feat/frontend/chat-cold-start-fix` → superseded by P0 fix above. Archive.
- `feat/frontend/hebrew-rtl-default` → if RTL isn't fully working on main, merge this.
- `feat/frontend/visual-polish` → merge any improvements not already on main.
- `chore/infra/workspace-stabilization` → assess and merge the safe parts.
- `release/phase-1-integration` → this appears to be a staging/integration branch.
  Confirm if it's tracking main; if so, delete.

---

### P5 — Continue previous in-flight missions

Continue (or monitor) all missions from `RESUME-README.md`:

- **Memory (04)**: real Postgres + Voyage embeddings. Check if `feat/agents/03-phase3-system-agents`
  has memory hydration improvements to cherry-pick.
- **GraphRAG (05)**: entity resolution + reranker. Track if `feat/curriculum/openstax-ingest`
  has ingest improvements.
- **MCP (06)**: assess `feat/mcp/05-server-improvements` and merge.
- **Evals (08)**: ensure Tutor evals gate is healthy in CI. Add section-reader
  evals once content pipeline is shipped.
- **Security (10)**: RBAC tests + PII pipeline. Prioritise before marketing push.

---

## Execution notes

- Work in small, atomic PRs. Conventional commit titles. `review-bugbot` on each.
- `review-security` on any PR touching auth, memory, RBAC, or encryption.
- If a Resend or R2 secret is needed and not set: add `sync: false` in `render.yaml`,
  add to `.env.example`, document in `BLOCKED.md`, and implement graceful degradation
  (log to DB only / skip PDF upload). Never block deployment on missing optional secrets.
- **Never message the user** mid-flight except in `BLOCKED.md` for strictly human-only
  secrets (e.g., login credentials for third-party dashboards).
- Update `docs/sprint.md` at the end of each session.

## Done when

1. Chat works with real AI responses (not mock fallback).
2. `/learn` content browser is live with browsable sections and Bagrut PDF viewer.
3. `/book` booking page is live with working form (email or DB-persisted).
4. In-flight branches triaged (merged, PRed, or deleted with a note).
5. CI green on `main`.

---

## Build error log (2026-06-25 13:31)

**Error**: Vercel build failed � "Command 'pnpm --filter @asf/web build' exited with 1"
**Root cause**: eact-markdown v9, emark-math v6, ehype-katex v7, ehype-highlight v7,
emark-gfm v4, and their unified/micromark transitive deps are **pure-ESM** packages.
Next.js cannot equire() them without explicit 	ranspilePackages entries.
**Fix applied**: 531a227 fix(frontend): add ESM-only remark/rehype packages to transpilePackages
**Lesson logged**: skills/add-a-frontend-page/SKILL.md � "ESM-only packages" section added.

**Rule for future sub-agents**: whenever adding a markdown/unified/remark/rehype package,
immediately add it (and its transitive deps) to 	ranspilePackages in 
ext.config.mjs.
