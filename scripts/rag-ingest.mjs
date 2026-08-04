#!/usr/bin/env node
/**
 * Offline RAG ingestion: chunk the authored lesson corpus (bilingual), embed each
 * chunk with nvidia/nv-embedqa-e5-v5 (1024-dim, input_type=passage), and
 * idempotently upsert into kg_chunks on the target Neon branch.
 *
 * Idempotent: chunk id is deterministic and content_hash gates re-embedding —
 * unchanged chunks are skipped (no wasted embedding calls) on re-runs.
 *
 * Requires the TLS-proxy workaround locally:
 *   node --use-system-ca scripts/rag-ingest.mjs            # ingest (dev)
 *   node --use-system-ca scripts/rag-ingest.mjs --limit 5  # smoke a few lessons
 *   node --use-system-ca scripts/rag-ingest.mjs --force    # allow non-dev host
 *
 * Reads DATABASE_URL + NVIDIA_API_KEY from env or apps/web/.env.local.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { normalizeLesson, validateLesson } from './lib/normalize-lesson.mjs';
import { makeEmbedder, EMBED_DIM } from './lib/rag-embed.mjs';

const ROOT = process.cwd();
const WEB = path.join(ROOT, 'apps/web');
const require = createRequire(path.join(WEB, 'package.json'));
const { neon } = require('@neondatabase/serverless');

const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const KG_DATA = path.join(WEB, 'src/lib/kg-data.json');

const FORCE = process.argv.includes('--force');
const argLimit = (() => {
  const i = process.argv.indexOf('--limit');
  return i >= 0 ? parseInt(process.argv[i + 1], 10) : 0;
})();

const DEV_HOST_MARKER = 'ep-purple-term';
const PROD_HOST_MARKERS = ['ep-plain-sea'];
const EMBED_BATCH = 32;
const UPSERT_BATCH = 50;

function env(key) {
  if (process.env[key]) return process.env[key];
  const text = fs.readFileSync(path.join(WEB, '.env.local'), 'utf-8');
  for (const line of text.split(/\r?\n/)) {
    const m = line.match(new RegExp(`^${key}\\s*=\\s*(.+)$`));
    if (m) return m[1].trim().replace(/^["']|["']$/g, '');
  }
  return undefined;
}

const url = env('DATABASE_URL');
if (!url) throw new Error('DATABASE_URL not found');
const host = (() => {
  try {
    return new URL(url).hostname;
  } catch {
    return '';
  }
})();
if (PROD_HOST_MARKERS.some((m) => host.includes(m)) && !FORCE) {
  console.error('REFUSING: target looks like PRODUCTION. Pass --force if intentional.');
  process.exit(1);
}
if (!host.includes(DEV_HOST_MARKER) && !FORCE) {
  console.error(`REFUSING: target host is not the DEV branch (${DEV_HOST_MARKER}). Pass --force to override.`);
  process.exit(1);
}

const sql = neon(url);
const embedder = makeEmbedder({ apiKey: env('NVIDIA_API_KEY'), baseUrl: env('NVIDIA_BASE_URL') });

const kgIds = (() => {
  try {
    const kg = JSON.parse(fs.readFileSync(KG_DATA, 'utf-8'));
    const nodes = Array.isArray(kg) ? kg : (kg.concepts ?? kg.nodes ?? []);
    return new Set(nodes.map((n) => n.id).filter(Boolean));
  } catch {
    return new Set();
  }
})();

const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');
const approxTokens = (s) => Math.ceil(s.length / 4);

/** Split long text into ~1200-char chunks on paragraph boundaries. */
function splitText(text, maxChars = 1400) {
  const t = text.trim();
  if (t.length <= maxChars) return [t];
  const paras = t.split(/\n{2,}/);
  const chunks = [];
  let cur = '';
  for (const p of paras) {
    if ((cur + '\n\n' + p).length > maxChars && cur) {
      chunks.push(cur.trim());
      cur = p;
    } else {
      cur = cur ? cur + '\n\n' + p : p;
    }
  }
  if (cur.trim()) chunks.push(cur.trim());
  // Hard-split any residual over-long chunk.
  const out = [];
  for (const c of chunks) {
    if (c.length <= maxChars * 1.5) {
      out.push(c);
    } else {
      for (let i = 0; i < c.length; i += maxChars) out.push(c.slice(i, i + maxChars));
    }
  }
  return out;
}

/**
 * Section kinds that carry teachable THEORY worth grounding answers on.
 * Assessment kinds (checkpoint, exercise_set, exam_problems) are intentionally
 * excluded — they are questions, not knowledge, and would bloat the index.
 */
const THEORY_KINDS = new Set([
  'intro',
  'definition',
  'theory',
  'worked_example',
  'method_guide',
  'pitfall',
  'practice_tip',
  'before_exam',
  'summary',
  'why_matters',
]);

/** Build language-specific chunk records for one lesson. */
function lessonChunks(lesson) {
  const records = [];
  const conceptId = lesson.concept_id;
  const linkedConcept = kgIds.has(conceptId) ? conceptId : null;
  const base = {
    source_type: 'lesson',
    source_doc_id: conceptId,
    concept_id: linkedConcept,
  };

  for (const lang of ['en', 'he']) {
    const lessonTitle = (lang === 'en' ? lesson.title_en : lesson.title_he) || '';
    const pieces = [];
    const summary = lang === 'en' ? lesson.summary_en : lesson.summary_he;
    if (summary?.trim()) pieces.push({ heading: lang === 'en' ? 'Summary' : 'תקציר', text: summary });

    for (const s of lesson.sections ?? []) {
      if (!THEORY_KINDS.has(s.kind)) continue;
      const title = lang === 'en' ? s.title_en : s.title_he;
      const body = lang === 'en' ? s.body_en_md : s.body_he_md;
      if (body?.trim()) {
        for (const part of splitText(body)) pieces.push({ heading: title, text: part });
      }
    }

    pieces.forEach((p, ordinal) => {
      const body = p.text.trim();
      // Enrich indexed text with concept + section name so retrieval (dense,
      // FTS, and trigram) can anchor on the topic even when the body prose does
      // not repeat it. This is the single biggest recall win, esp. for Hebrew.
      const prefix = [lessonTitle, p.heading].filter((x) => x && x.trim()).join(' — ');
      const text = prefix ? `${prefix}\n\n${body}` : body;
      const id = `${base.source_type}:${base.source_doc_id}:${lang}:${ordinal}`;
      records.push({
        id: id.slice(0, 160),
        document_id: base.source_doc_id,
        source_type: base.source_type,
        source_doc_id: base.source_doc_id,
        concept_id: base.concept_id,
        lang,
        ordinal,
        heading: (p.heading || '').slice(0, 512),
        text,
        token_count: approxTokens(text),
        content_hash: sha(`${id}|${text}`),
        provenance: {
          subject: lesson.subject,
          level: lesson.level,
          math_track: lesson.math_track,
          title: lang === 'en' ? lesson.title_en : lesson.title_he,
        },
      });
    });
  }
  return records;
}

async function main() {
  console.log(`target: ${host}`);
  console.log(`embedding model: nvidia/nv-embedqa-e5-v5 (${EMBED_DIM}d, passage)`);

  let files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
  if (argLimit > 0) files = files.slice(0, argLimit);

  // 1) build all chunk records (health-gate: skip schema-invalid lessons)
  const all = [];
  let skipped = 0;
  for (const file of files) {
    let raw;
    try {
      raw = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, file), 'utf-8'));
    } catch {
      skipped += 1;
      continue;
    }
    const lesson = normalizeLesson(raw, file);
    if (validateLesson(file, lesson).length > 0) {
      skipped += 1;
      continue;
    }
    all.push(...lessonChunks(lesson));
  }
  console.log(`lessons: ${files.length} (skipped ${skipped}) -> ${all.length} chunks`);

  // optional clean slate (removes stale rows from prior chunking strategies)
  if (process.argv.includes('--fresh')) {
    await sql`TRUNCATE TABLE kg_chunks`;
    console.log('truncated kg_chunks (--fresh)');
  }

  // 2) idempotency: load existing id->content_hash
  const existing = new Map();
  const existingRows = await sql`SELECT id, content_hash FROM kg_chunks`;
  for (const r of existingRows) existing.set(r.id, r.content_hash);

  const pending = all.filter((c) => existing.get(c.id) !== c.content_hash);
  console.log(`to embed/upsert: ${pending.length} (unchanged: ${all.length - pending.length})`);

  // 3) embed in batches (passage)
  let embedded = 0;
  for (let i = 0; i < pending.length; i += EMBED_BATCH) {
    const batch = pending.slice(i, i + EMBED_BATCH);
    const vecs = await embedder.embedBatch(batch.map((c) => c.text), 'passage');
    batch.forEach((c, j) => {
      c.embedding = vecs[j];
    });
    embedded += batch.length;
    if (i % (EMBED_BATCH * 10) === 0 || embedded >= pending.length) {
      console.log(`  embedded ${embedded}/${pending.length}`);
    }
  }

  // 4) upsert in transaction batches
  let upserted = 0;
  for (let i = 0; i < pending.length; i += UPSERT_BATCH) {
    const batch = pending.slice(i, i + UPSERT_BATCH);
    const queries = batch.map((c) => {
      const vecStr = `[${c.embedding.join(',')}]`;
      return sql`
        INSERT INTO kg_chunks
          (id, document_id, source_type, source_doc_id, concept_id, lang, ordinal,
           heading, text, token_count, content_hash, embedding, provenance)
        VALUES
          (${c.id}, ${c.document_id}, ${c.source_type}, ${c.source_doc_id}, ${c.concept_id},
           ${c.lang}, ${c.ordinal}, ${c.heading}, ${c.text}, ${c.token_count},
           ${c.content_hash}, ${vecStr}::vector, ${JSON.stringify(c.provenance)}::jsonb)
        ON CONFLICT (id) DO UPDATE SET
          document_id = EXCLUDED.document_id,
          source_type = EXCLUDED.source_type,
          source_doc_id = EXCLUDED.source_doc_id,
          concept_id = EXCLUDED.concept_id,
          lang = EXCLUDED.lang,
          ordinal = EXCLUDED.ordinal,
          heading = EXCLUDED.heading,
          text = EXCLUDED.text,
          token_count = EXCLUDED.token_count,
          content_hash = EXCLUDED.content_hash,
          embedding = EXCLUDED.embedding,
          provenance = EXCLUDED.provenance
      `;
    });
    await sql.transaction(queries);
    upserted += batch.length;
    if (i % (UPSERT_BATCH * 5) === 0 || upserted >= pending.length) {
      console.log(`  upserted ${upserted}/${pending.length}`);
    }
  }

  // 5) summary
  const stats = await sql`
    SELECT lang, source_type,
           COUNT(*)::int AS n,
           COUNT(embedding)::int AS with_vec
    FROM kg_chunks GROUP BY lang, source_type ORDER BY lang, source_type`;
  console.log('\n=== kg_chunks summary ===');
  for (const r of stats) console.log(`  ${r.lang}/${r.source_type}: ${r.n} rows (${r.with_vec} embedded)`);
  const total = await sql`SELECT COUNT(*)::int AS n FROM kg_chunks`;
  console.log(`  TOTAL: ${total[0].n}`);
  console.log('\nOK — ingestion complete.');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
