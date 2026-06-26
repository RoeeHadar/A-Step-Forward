# Skill: In-house concept content (scraped + attributed)

**When to use**: any time the Learn section needs new explanatory content per
concept, or a coordinator/sub-agent asks to "fix the Learn page so we host
content natively instead of linking out."

This skill documents the end-to-end pipeline for **scraping, adapting and
rendering bilingual (EN + HE) concept explanations** sourced from CC-licensed
public material (currently Wikipedia, CC BY-SA 4.0). The pipeline is designed
so a non-engineer (or a sub-agent) can extend it with one YAML edit and one
workflow run — no code changes required.

---

## The pipeline at a glance

```
Knowledge Graph YAMLs (content/knowledge-graph/*.yaml)
         │
         │  scripts/build-kg-json.mjs           (sync to apps/web/src/lib/kg-data.json)
         ▼
Static KG snapshot used by Vercel + scraper
         │
         │  scripts/scrape-concept-content.mjs  (uses content/concept-wikipedia-overrides.yaml)
         │  Wikipedia REST API: EN + HE, summary + first sections
         │  Adapts HTML → markdown, strips citations, keeps attribution
         ▼
Neon table: concept_explanations
   (concept_id, language, title, body_md, body_html, summary, image_url,
    source, source_url, license, attribution, fetched_at)
         │
         │  Read via apps/web/src/lib/neon-db.ts helpers
         ▼
UI: /learn/[subject]/concept/[conceptId]
   - Language toggle (EN / HE)
   - Markdown body, image, summary
   - Mandatory attribution footer + license
   - "Continue to source" link
   - "Ask the AI Tutor" CTA
```

## Files you touch

| File | Purpose |
| --- | --- |
| `content/concept-wikipedia-overrides.yaml` | Explicit Wikipedia article titles per concept when auto-search returns the wrong page. Edit when a concept page shows the wrong content. |
| `infra/alembic/versions/0012_concept_explanations.py` | Schema for `concept_explanations`. **Do not edit** — add a new migration if shape changes. |
| `scripts/scrape-concept-content.mjs` | Scraper. Idempotent. Reads KG, fetches Wikipedia EN + HE, upserts. |
| `apps/web/src/lib/neon-db.ts` | Reader helpers: `fetchConceptExplanation`, `fetchConceptExplanationFallback`, `fetchConceptsWithExplanations`. |
| `apps/web/src/app/learn/[subject]/concept/[conceptId]/page.tsx` | Server page. Loads EN + HE in parallel. |
| `apps/web/src/components/concept-content-client.tsx` | Renders content with language toggle + attribution. |
| `apps/web/src/app/learn/[subject]/page.tsx` | Lists concepts per subject with EN/HE coverage badges. |
| `.github/workflows/seed-db.yml` | Run the scraper from GitHub Actions: workflow_dispatch → target = `concept-explanations`. |

## Adding a new source (e.g. OpenStax)

1. Schema is already source-aware (`source`, `source_url`, `license`,
   `attribution`). The unique constraint is `(concept_id, language, source)`,
   so multiple sources can coexist per concept.
2. Add a new fetcher function in `scripts/scrape-concept-content.mjs` (e.g.
   `fetchOpenStaxSection`). Reuse `upsert(row)`.
3. The UI already picks the highest-quality available source automatically.
   If you want explicit per-source UI variants, extend
   `concept-content-client.tsx` to accept a `Map<source, Explanation[]>`
   instead of just `en`/`he`.
4. Add the scraper invocation to `.github/workflows/seed-db.yml` under a new
   target name.

## License & attribution checklist (per source)

Before adding a new source, verify:

- [ ] License **permits adaptation** (CC BY, CC BY-SA, CC0, public domain).
- [ ] License does **not** require non-commercial only (we intend a paid tier).
  - ✅ CC BY 4.0, CC BY-SA 4.0, CC0, PD
  - ❌ CC BY-NC, CC BY-NC-SA (avoid)
- [ ] Source URL is stable and dereferenceable.
- [ ] Title + license + URL are stored on every row.
- [ ] UI shows attribution prominently (not hidden in a footer link).
- [ ] If the source license is share-alike (BY-SA), any user-facing remix is
      also share-alike. Document this on the page.

## Running the scraper

**From GitHub Actions** (preferred — uses production secrets):

```
Actions → Seed Neon → Run workflow → target: concept-explanations
```

**Locally** (requires Neon access — corporate proxies may block):

```bash
DATABASE_URL=postgresql://... node scripts/scrape-concept-content.mjs
# Or fix a single bad concept:
DATABASE_URL=... node scripts/scrape-concept-content.mjs --only=eigenvalues --force
# Dry run:
DATABASE_URL=... node scripts/scrape-concept-content.mjs --dry-run
```

## When a concept page shows the wrong content

1. Visit `/learn/<subject>/concept/<concept_id>` and confirm the issue.
2. Look up the correct Wikipedia article title in EN and/or HE.
3. Add (or update) the entry in `content/concept-wikipedia-overrides.yaml`.
4. Run the seed workflow with `target: concept-explanations` (it re-runs
   only the affected rows because the scraper skips by default; use
   `--force` locally for a single concept).

## When a concept has no content

The page renders a graceful placeholder ("No explanation has been ingested
yet") and links to the AI Tutor. This is safe — no broken-link experience.

To remedy:

- Add an override mapping in `content/concept-wikipedia-overrides.yaml`.
- Or extend `scripts/scrape-concept-content.mjs` to try synonyms / alternative
  search queries.

## What not to do

- ❌ Don't paste outbound links to external teaching sites and call it done.
- ❌ Don't store source content without `source_url`, `license`, and
  `attribution` fields.
- ❌ Don't strip Wikipedia citations silently in body text without the
  attribution footer; the footer is **required** by CC BY-SA.
- ❌ Don't add Khan Academy article scraping — KA articles are CC BY-NC-SA
  (non-commercial only). Their videos are fine to *embed* via official
  embed APIs.
