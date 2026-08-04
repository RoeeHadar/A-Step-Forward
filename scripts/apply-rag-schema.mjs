#!/usr/bin/env node
/**
 * Apply the RAG chunk schema to a Neon branch via the serverless HTTP driver.
 *
 * This is the Neon-direct equivalent of Alembic migration
 * `infra/alembic/versions/0024_kg_chunks_rag.py`. We apply it directly here
 * because the local Python/uv toolchain cannot bootstrap through the corporate
 * TLS-intercepting proxy. Every statement is idempotent (IF NOT EXISTS), so:
 *   - re-running is a no-op, and
 *   - a later `alembic upgrade head` (CI / prod) still applies 0024 cleanly.
 *
 * It also ensures the base `kg_chunks` table + `vector` extension exist, so it
 * works even on a Neon branch that never had the earlier migrations applied.
 *
 * SAFETY: refuses to run unless the target host looks like the DEV branch
 * (ep-purple-term…) unless you pass --force. It prints a masked host first.
 *
 * Usage (reads DATABASE_URL from env or apps/web/.env.local):
 *   node scripts/apply-rag-schema.mjs
 *   node scripts/apply-rag-schema.mjs --force   # allow non-dev host
 */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = process.cwd();
const WEB = path.join(ROOT, 'apps/web');
const require = createRequire(path.join(WEB, 'package.json'));
const { neon } = require('@neondatabase/serverless');

const FORCE = process.argv.includes('--force');
const DEV_HOST_MARKER = 'ep-purple-term';
const PROD_HOST_MARKERS = ['ep-plain-sea'];

function resolveDatabaseUrl() {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;
  const envFile = path.join(WEB, '.env.local');
  const text = fs.readFileSync(envFile, 'utf-8');
  for (const line of text.split(/\r?\n/)) {
    const m = line.match(/^DATABASE_URL\s*=\s*(.+)$/);
    if (m) return m[1].trim().replace(/^["']|["']$/g, '');
  }
  throw new Error('DATABASE_URL not found in env or apps/web/.env.local');
}

function maskHost(url) {
  try {
    const u = new URL(url);
    return `${u.hostname}${u.pathname}`;
  } catch {
    return '(unparseable url)';
  }
}

const url = resolveDatabaseUrl();
const host = (() => {
  try {
    return new URL(url).hostname;
  } catch {
    return '';
  }
})();

console.log(`target: ${maskHost(url)}`);

if (PROD_HOST_MARKERS.some((m) => host.includes(m)) && !FORCE) {
  console.error('REFUSING: target looks like PRODUCTION. Pass --force only if intentional.');
  process.exit(1);
}
if (!host.includes(DEV_HOST_MARKER) && !FORCE) {
  console.error(
    `REFUSING: target host does not look like the DEV branch (${DEV_HOST_MARKER}). Pass --force to override.`,
  );
  process.exit(1);
}

const sql = neon(url);

/**
 * Run a raw SQL string through the neon tagged-template (older driver versions
 * don't expose `sql.query`). We hand it a proper template-strings array (with a
 * `.raw` prop) and no interpolated values, so the text is used verbatim.
 */
function run(text) {
  const strings = [text];
  strings.raw = [text];
  return sql(strings);
}

// Ordered statements. Mirrors Alembic 0024_kg_chunks_rag: recreate kg_chunks
// as the bilingual hybrid-RAG store at vector(1024) for nvidia/nv-embedqa-e5-v5.
// kg_chunks is empty everywhere (unused GraphRAG path), so drop+recreate is safe.
const RECREATE = process.argv.includes('--recreate');
const statements = [
  ['ext: vector', 'CREATE EXTENSION IF NOT EXISTS vector'],
  ['ext: pg_trgm', 'CREATE EXTENSION IF NOT EXISTS pg_trgm'],
  ...(RECREATE ? [['drop: kg_chunks (empty)', 'DROP TABLE IF EXISTS kg_chunks']] : []),
  [
    'table: kg_chunks (rag @1024)',
    `CREATE TABLE IF NOT EXISTS kg_chunks (
      id VARCHAR(160) PRIMARY KEY,
      document_id VARCHAR(128) NOT NULL,
      source_type VARCHAR(32) NOT NULL,
      source_doc_id VARCHAR(128) NOT NULL,
      concept_id VARCHAR(128),
      lang VARCHAR(8) NOT NULL,
      ordinal INTEGER NOT NULL,
      heading VARCHAR(512),
      text TEXT NOT NULL,
      token_count INTEGER,
      content_hash VARCHAR(64),
      embedding vector(1024),
      provenance JSONB,
      tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(text, ''))) STORED,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`,
  ],
  [
    'idx: embedding hnsw',
    'CREATE INDEX IF NOT EXISTS kg_chunks_embedding_hnsw_idx ON kg_chunks USING hnsw (embedding vector_cosine_ops)',
  ],
  ['idx: tsv gin', 'CREATE INDEX IF NOT EXISTS kg_chunks_tsv_idx ON kg_chunks USING gin (tsv)'],
  ['idx: text trgm', 'CREATE INDEX IF NOT EXISTS kg_chunks_text_trgm_idx ON kg_chunks USING gin (text gin_trgm_ops)'],
  ['idx: source', 'CREATE INDEX IF NOT EXISTS kg_chunks_source_idx ON kg_chunks (source_type, source_doc_id)'],
  ['idx: concept_id', 'CREATE INDEX IF NOT EXISTS kg_chunks_concept_id_idx ON kg_chunks (concept_id)'],
  ['idx: lang', 'CREATE INDEX IF NOT EXISTS kg_chunks_lang_idx ON kg_chunks (lang)'],
  ['idx: content_hash', 'CREATE INDEX IF NOT EXISTS kg_chunks_content_hash_idx ON kg_chunks (content_hash)'],
  ['idx: document_id', 'CREATE INDEX IF NOT EXISTS kg_chunks_document_id_idx ON kg_chunks (document_id)'],
];

async function main() {
  console.log('\napplying RAG schema (idempotent)…');
  for (const [label, stmt] of statements) {
    try {
      await run(stmt);
      console.log(`  ok    ${label}`);
    } catch (e) {
      console.error(`  FAIL  ${label}: ${e.message}`);
      throw e;
    }
  }

  // --- verify ---
  console.log('\nverifying…');
  const cols = await run(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'kg_chunks' ORDER BY column_name",
  );
  const idx = await run(
    "SELECT indexname FROM pg_indexes WHERE tablename = 'kg_chunks' ORDER BY indexname",
  );
  const ext = await run(
    "SELECT extname FROM pg_extension WHERE extname IN ('vector','pg_trgm') ORDER BY extname",
  );

  const colNames = cols.map((r) => r.column_name);
  const idxNames = idx.map((r) => r.indexname);
  const extNames = ext.map((r) => r.extname);

  const requiredCols = ['lang', 'source_type', 'source_doc_id', 'concept_id', 'content_hash', 'tsv', 'embedding'];
  // vector(1024): pg_attribute.atttypmod carries the declared dimension.
  const dimRows = await run(
    "SELECT a.atttypmod AS dim FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid WHERE c.relname = 'kg_chunks' AND a.attname = 'embedding'",
  );
  const embDim = dimRows[0]?.dim;
  console.log(`  embedding dim: ${embDim}`);
  if (embDim !== 1024) {
    console.error(`\nWRONG DIM — embedding is ${embDim}, expected 1024. Re-run with --recreate.`);
    process.exit(1);
  }
  const requiredIdx = [
    'kg_chunks_lang_idx',
    'kg_chunks_source_idx',
    'kg_chunks_concept_id_idx',
    'kg_chunks_content_hash_idx',
    'kg_chunks_text_trgm_idx',
    'kg_chunks_tsv_idx',
    'kg_chunks_embedding_hnsw_idx',
  ];

  const missingCols = requiredCols.filter((c) => !colNames.includes(c));
  const missingIdx = requiredIdx.filter((i) => !idxNames.includes(i));

  console.log(`  extensions: ${extNames.join(', ') || '(none)'}`);
  console.log(`  columns:    ${colNames.join(', ')}`);
  console.log(`  indexes:    ${idxNames.join(', ')}`);

  if (missingCols.length || missingIdx.length || !extNames.includes('vector') || !extNames.includes('pg_trgm')) {
    console.error(
      `\nINCOMPLETE — missing cols: [${missingCols.join(', ')}] missing idx: [${missingIdx.join(', ')}]`,
    );
    process.exit(1);
  }

  console.log('\nOK — kg_chunks is ready for bilingual hybrid RAG on the dev branch.');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
