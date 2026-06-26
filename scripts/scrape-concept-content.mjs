#!/usr/bin/env node
/**
 * Scrape Wikipedia article summaries for every KG concept (EN + HE) and store
 * them in the concept_explanations table.
 *
 * Content is fetched via the official Wikipedia REST API and adapted (truncated
 * to a useful length, light markdown cleanup, attribution preserved). Wikipedia
 * content is CC BY-SA 4.0 — by storing + displaying with attribution we comply.
 *
 * Usage:
 *   DATABASE_URL=postgresql://... node scripts/scrape-concept-content.mjs
 *
 *   --only=<concept_id>     fetch a single concept (useful for fixing one bad match)
 *   --langs=en,he           override the languages to fetch (default both)
 *   --force                 refetch even if (concept_id, language, source) already exists
 *   --dry-run               print what would happen, no DB writes
 *
 * Idempotent — uses ON CONFLICT (concept_id, language, source) DO UPDATE.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as sleep } from 'node:timers/promises';
import * as yaml from 'js-yaml';
import { neon } from '@neondatabase/serverless';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const USER_AGENT =
  'AStepForwardLearningCenter/1.0 (https://a-step-forward-waij.vercel.app; contact@a-step-forward.example)';
const REQUEST_DELAY_MS = 120; // ~8 req/s, well under Wikipedia limits

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}
const sql = neon(url);

// ── Args ────────────────────────────────────────────────────────────────────
const args = new Map();
for (const arg of process.argv.slice(2)) {
  const [k, v] = arg.startsWith('--') ? arg.slice(2).split('=') : [];
  if (k) args.set(k, v ?? 'true');
}
const onlyConcept = args.get('only') ?? null;
const langs = (args.get('langs') ?? 'en,he').split(',').map((s) => s.trim()).filter(Boolean);
const force = args.get('force') === 'true';
const dryRun = args.get('dry-run') === 'true';

// ── Load KG + overrides ─────────────────────────────────────────────────────
const kg = JSON.parse(
  fs.readFileSync(path.join(ROOT, 'apps', 'web', 'src', 'lib', 'kg-data.json'), 'utf-8'),
);
const overridesYaml = yaml.load(
  fs.readFileSync(path.join(ROOT, 'content', 'concept-wikipedia-overrides.yaml'), 'utf-8'),
);
const overrides = overridesYaml?.overrides ?? {};

const concepts = onlyConcept
  ? kg.concepts.filter((c) => c.id === onlyConcept)
  : kg.concepts;

if (onlyConcept && concepts.length === 0) {
  console.error(`No concept with id="${onlyConcept}" in kg-data.json`);
  process.exit(1);
}

console.log(`Scraping ${concepts.length} concepts × ${langs.join('+')} from Wikipedia\n`);

// ── Wikipedia helpers ───────────────────────────────────────────────────────
async function wikipediaFetch(lang, urlPath) {
  const resp = await fetch(`https://${lang}.wikipedia.org${urlPath}`, {
    headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' },
  });
  if (!resp.ok) throw new Error(`Wikipedia ${lang} ${resp.status} on ${urlPath}`);
  return resp.json();
}

async function findTitle(lang, query) {
  const data = await wikipediaFetch(
    lang,
    `/w/api.php?action=opensearch&search=${encodeURIComponent(query)}&limit=1&format=json&namespace=0`,
  );
  return data?.[1]?.[0] ?? null;
}

async function fetchSummary(lang, title) {
  return wikipediaFetch(
    lang,
    `/api/rest_v1/page/summary/${encodeURIComponent(title.replace(/ /g, '_'))}`,
  );
}

async function fetchSections(lang, title) {
  // Get the first 2 leading sections of the article (richer than summary alone).
  try {
    const data = await wikipediaFetch(
      lang,
      `/api/rest_v1/page/mobile-sections-lead/${encodeURIComponent(title.replace(/ /g, '_'))}`,
    );
    return data?.sections ?? [];
  } catch {
    return [];
  }
}

function htmlToMarkdown(html) {
  if (!html) return '';
  // Very lightweight HTML → markdown adaptation. Wikipedia summaries are short
  // and predominantly text; we keep paragraphs, lists, emphasis, links.
  let md = html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    // citations like <sup class="reference">[1]</sup>
    .replace(/<sup[^>]*class="[^"]*reference[^"]*"[^>]*>[\s\S]*?<\/sup>/gi, '')
    .replace(/<sup[^>]*>\[[\s\S]*?\]<\/sup>/gi, '')
    // <a href="/wiki/..."> turned into bare text (we don't link out per-paragraph)
    .replace(/<a[^>]*>([\s\S]*?)<\/a>/gi, '$1')
    .replace(/<b>([\s\S]*?)<\/b>/gi, '**$1**')
    .replace(/<strong>([\s\S]*?)<\/strong>/gi, '**$1**')
    .replace(/<i>([\s\S]*?)<\/i>/gi, '*$1*')
    .replace(/<em>([\s\S]*?)<\/em>/gi, '*$1*')
    .replace(/<li>([\s\S]*?)<\/li>/gi, '- $1\n')
    .replace(/<\/?ul[^>]*>/gi, '\n')
    .replace(/<\/?ol[^>]*>/gi, '\n')
    .replace(/<\/?p[^>]*>/gi, '\n\n')
    .replace(/<br\s*\/?\s*>/gi, '\n')
    .replace(/<[^>]+>/g, '') // strip remaining tags
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
  return md;
}

async function fetchConceptInLang(concept, lang) {
  // 1) Determine the article title
  const override = overrides[concept.id]?.[lang];
  if (overrides[concept.id]?.skip) return null;

  let title = override;
  if (!title) {
    const query = lang === 'he' && concept.name_he ? concept.name_he : concept.name;
    title = await findTitle(lang, query);
    if (!title) {
      // try alt: replace em-dash, strip parentheticals
      const alt = concept.name.replace(/—/g, '-').replace(/\([^)]*\)/g, '').trim();
      if (alt && alt !== query) {
        title = await findTitle(lang, alt);
      }
    }
  }
  if (!title) return null;

  // 2) Fetch summary
  let summary;
  try {
    summary = await fetchSummary(lang, title);
  } catch (err) {
    console.warn(`  [${lang}] summary failed for "${title}": ${err.message}`);
    return null;
  }
  // Disambiguation pages or empty extracts → skip
  if (summary.type === 'disambiguation' || !summary.extract) return null;

  // 3) Optionally enrich with the first few section paragraphs
  const sections = await fetchSections(lang, title).catch(() => []);
  let bodyHtml = summary.extract_html ?? '';
  for (const section of (sections ?? []).slice(0, 3)) {
    if (section?.text) {
      bodyHtml += '\n' + section.text;
    }
  }

  const bodyMd = htmlToMarkdown(bodyHtml || summary.extract);
  const truncated = bodyMd.length > 8000 ? bodyMd.slice(0, 8000) + '\n\n_...continued in source._' : bodyMd;

  const sourceUrl =
    summary.content_urls?.desktop?.page ??
    `https://${lang}.wikipedia.org/wiki/${encodeURIComponent(title.replace(/ /g, '_'))}`;

  return {
    concept_id: concept.id,
    language: lang,
    title: summary.displaytitle?.replace(/<[^>]+>/g, '') ?? title,
    body_md: truncated,
    body_html: bodyHtml || null,
    summary: summary.description ?? summary.extract?.slice(0, 280) ?? null,
    image_url: summary.thumbnail?.source ?? null,
    source: 'wikipedia',
    source_url: sourceUrl,
    source_lang: lang,
    license: 'CC BY-SA 4.0',
    attribution: `Adapted from "${summary.displaytitle?.replace(/<[^>]+>/g, '') ?? title}" on Wikipedia, available under the Creative Commons Attribution-ShareAlike 4.0 License. Source: ${sourceUrl}`,
  };
}

async function alreadyHave(conceptId, language) {
  const rows = await sql`
    SELECT 1 FROM concept_explanations
    WHERE concept_id = ${conceptId} AND language = ${language} AND source = 'wikipedia'
    LIMIT 1
  `;
  return rows.length > 0;
}

async function upsert(row) {
  await sql`
    INSERT INTO concept_explanations (
      id, concept_id, language, title, body_md, body_html, summary, image_url,
      source, source_url, source_lang, license, attribution, fetched_at
    ) VALUES (
      gen_random_uuid(), ${row.concept_id}, ${row.language}, ${row.title},
      ${row.body_md}, ${row.body_html}, ${row.summary}, ${row.image_url},
      ${row.source}, ${row.source_url}, ${row.source_lang}, ${row.license},
      ${row.attribution}, NOW()
    )
    ON CONFLICT (concept_id, language, source) DO UPDATE SET
      title = EXCLUDED.title,
      body_md = EXCLUDED.body_md,
      body_html = EXCLUDED.body_html,
      summary = EXCLUDED.summary,
      image_url = EXCLUDED.image_url,
      source_url = EXCLUDED.source_url,
      attribution = EXCLUDED.attribution,
      fetched_at = NOW()
  `;
}

// ── Main loop ───────────────────────────────────────────────────────────────
let fetched = 0;
let written = 0;
let skipped = 0;
let errors = 0;

for (const concept of concepts) {
  for (const lang of langs) {
    if (!force && !dryRun) {
      if (await alreadyHave(concept.id, lang)) {
        skipped += 1;
        continue;
      }
    }
    try {
      const row = await fetchConceptInLang(concept, lang);
      if (!row) {
        console.warn(`  - [${lang}] no article for ${concept.id} (${concept.name})`);
        skipped += 1;
        continue;
      }
      fetched += 1;
      console.log(`  + [${lang}] ${concept.id} → "${row.title}" (${row.body_md.length} chars)`);
      if (!dryRun) {
        await upsert(row);
        written += 1;
      }
    } catch (err) {
      errors += 1;
      console.error(`  ! [${lang}] ${concept.id}: ${err.message}`);
    }
    await sleep(REQUEST_DELAY_MS);
  }
}

console.log(`\nDone. fetched=${fetched} written=${written} skipped=${skipped} errors=${errors}`);
