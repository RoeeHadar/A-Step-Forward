#!/usr/bin/env node
/**
 * Retrieval sanity eval for the hybrid RAG store (recall@k + MRR).
 *
 * Mirrors apps/web/src/lib/rag-retrieve.ts (dense HNSW ⊕ lexical tsv → RRF) and
 * runs a small bilingual query set against the live dev kg_chunks. A test passes
 * when a retrieved chunk's doc id or title contains the expected keyword.
 *
 *   node --use-system-ca scripts/rag-eval.mjs
 *
 * Exit code is non-zero if recall@k falls below --min (default 0.75).
 */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { makeEmbedder } from './lib/rag-embed.mjs';

const ROOT = process.cwd();
const WEB = path.join(ROOT, 'apps/web');
const require = createRequire(path.join(WEB, 'package.json'));
const { neon } = require('@neondatabase/serverless');

function env(key) {
  if (process.env[key]) return process.env[key];
  const text = fs.readFileSync(path.join(WEB, '.env.local'), 'utf-8');
  for (const line of text.split(/\r?\n/)) {
    const m = line.match(new RegExp(`^${key}\\s*=\\s*(.+)$`));
    if (m) return m[1].trim().replace(/^["']|["']$/g, '');
  }
  return undefined;
}

const TOP_K = 6;
const CAND_K = 40;
const RRF_K = 60;
const MIN = (() => {
  const i = process.argv.indexOf('--min');
  return i >= 0 ? parseFloat(process.argv[i + 1]) : 0.75;
})();

const sql = neon(env('DATABASE_URL'));
const embedder = makeEmbedder({ apiKey: env('NVIDIA_API_KEY'), baseUrl: env('NVIDIA_BASE_URL') });

// Bilingual query set. `expect` is a keyword expected in a retrieved doc id/title.
const CASES = [
  { q: 'What are the rules for differentiating a product of functions?', lang: 'en', expect: 'rules' },
  { q: 'How does the chain rule work for composite functions?', lang: 'en', expect: 'chain' },
  { q: 'Explain the Pythagorean theorem', lang: 'en', expect: 'pythag' },
  { q: 'What is a limit of a function?', lang: 'en', expect: 'limit' },
  { q: 'How do I integrate by parts?', lang: 'en', expect: 'part' },
  { q: 'derivative of sine and cosine', lang: 'en', expect: 'deriv' },
  { q: 'מהם כללי הגזירה של מכפלת פונקציות?', lang: 'he', expect: 'rules' },
  { q: 'איך עובד כלל השרשרת בגזירה?', lang: 'he', expect: 'chain' },
  { q: 'מה זה גבול של פונקציה?', lang: 'he', expect: 'limit' },
  { q: 'משפט פיתגורס במשולש ישר זווית', lang: 'he', expect: 'pythag' },
  { q: 'אינטגרציה בחלקים', lang: 'he', expect: 'part' },
  { q: 'אינטגרל לא מסוים', lang: 'he', expect: 'integr' },
];

async function retrieve(q, lang, vec) {
  const vecStr = `[${vec.join(',')}]`;
  return sql`
    WITH dense AS (
      SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> ${vecStr}::vector) AS rnk
      FROM kg_chunks WHERE lang = ${lang} AND embedding IS NOT NULL
      ORDER BY embedding <=> ${vecStr}::vector LIMIT ${CAND_K}
    ),
    lex AS (
      SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(tsv, websearch_to_tsquery('simple', ${q})) DESC) AS rnk
      FROM kg_chunks WHERE lang = ${lang} AND tsv @@ websearch_to_tsquery('simple', ${q}) LIMIT ${CAND_K}
    ),
    trgm AS (
      SELECT id, ROW_NUMBER() OVER (ORDER BY word_similarity(${q}, text) DESC) AS rnk
      FROM kg_chunks WHERE lang = ${lang} AND word_similarity(${q}, text) > 0.1
      ORDER BY word_similarity(${q}, text) DESC LIMIT ${CAND_K}
    ),
    fused AS (
      SELECT id, SUM(w) AS score FROM (
        SELECT id, 1.0/(${RRF_K}+rnk) AS w FROM dense
        UNION ALL SELECT id, 1.0/(${RRF_K}+rnk) AS w FROM lex
        UNION ALL SELECT id, 1.0/(${RRF_K}+rnk) AS w FROM trgm
      ) u GROUP BY id
    )
    SELECT k.source_doc_id, k.provenance->>'title' AS title, f.score
    FROM fused f JOIN kg_chunks k ON k.id = f.id
    ORDER BY f.score DESC LIMIT ${TOP_K}`;
}

async function main() {
  let hits = 0;
  let mrrSum = 0;
  const lines = [];
  for (const c of CASES) {
    const [vec] = await embedder.embedBatch([c.q], 'query');
    const rows = await retrieve(c.q, c.lang, vec);
    const kw = c.expect.toLowerCase();
    let rank = 0;
    for (let i = 0; i < rows.length; i++) {
      const hay = `${rows[i].source_doc_id} ${rows[i].title ?? ''}`.toLowerCase();
      if (hay.includes(kw)) {
        rank = i + 1;
        break;
      }
    }
    if (rank > 0) {
      hits += 1;
      mrrSum += 1 / rank;
    }
    const top = rows[0] ? `${rows[0].source_doc_id}` : '(none)';
    lines.push(
      `  [${rank > 0 ? 'HIT@' + rank : 'MISS '}] (${c.lang}) "${c.q.slice(0, 42)}" expect=${c.expect} top=${top}`,
    );
  }
  const recall = hits / CASES.length;
  const mrr = mrrSum / CASES.length;
  console.log('=== RAG retrieval eval (recall@' + TOP_K + ') ===');
  for (const l of lines) console.log(l);
  console.log('');
  console.log(`recall@${TOP_K}: ${(recall * 100).toFixed(1)}%  (${hits}/${CASES.length})   MRR: ${mrr.toFixed(3)}`);
  if (recall < MIN) {
    console.error(`FAIL — recall ${(recall * 100).toFixed(1)}% < min ${(MIN * 100).toFixed(0)}%`);
    process.exit(1);
  }
  console.log('PASS');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
