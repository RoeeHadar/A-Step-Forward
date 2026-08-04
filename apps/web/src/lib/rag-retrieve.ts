/**
 * Hybrid RAG retrieval over kg_chunks (authored bilingual corpus).
 *
 * Dense channel : pgvector HNSW cosine over nvidia/nv-embedqa-e5-v5 (1024d).
 * Lexical channel: Postgres FTS (to_tsvector('simple')) + pg_trgm similarity.
 * Fusion        : Reciprocal Rank Fusion (RRF, k=60).
 *
 * Language-filtered (he/en) so Hebrew queries retrieve Hebrew passages and vice
 * versa. Degrades gracefully: if the embedding API is unavailable the dense
 * channel is skipped and results come from the lexical channel alone.
 */
import 'server-only';
import { neon } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';
import { embedQuery } from '@/lib/rag-embed';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

const RRF_K = 60;
const DEFAULT_TOP_K = 6;
const DEFAULT_CANDIDATE_K = 40;

export type RagLang = 'en' | 'he';

export interface RagChunk {
  id: string;
  text: string;
  heading: string | null;
  sourceType: string;
  sourceDocId: string;
  conceptId: string | null;
  title: string | null;
  score: number;
  channel: 'hybrid' | 'dense' | 'lexical';
}

export interface RetrieveOptions {
  query: string;
  lang?: RagLang;
  topK?: number;
  candidateK?: number;
  /** Restrict to a subject when known (matches provenance->>'subject'). */
  subject?: string;
}

const HEBREW_RE = /[\u0590-\u05FF]/;
export function detectLang(text: string): RagLang {
  return HEBREW_RE.test(text) ? 'he' : 'en';
}

interface Row {
  id: string;
  text: string;
  heading: string | null;
  source_type: string;
  source_doc_id: string;
  concept_id: string | null;
  title: string | null;
  score: number;
}

function toChunk(r: Row, channel: RagChunk['channel']): RagChunk {
  return {
    id: r.id,
    text: r.text,
    heading: r.heading,
    sourceType: r.source_type,
    sourceDocId: r.source_doc_id,
    conceptId: r.concept_id,
    title: r.title,
    score: Number(r.score),
    channel,
  };
}

/**
 * Cheap, cached readiness probe. RAG ships flag-ON, but a target DB may not have
 * the corpus ingested yet (e.g. prod before the ingest workflow runs). Without
 * this, every eligible turn would pay an embedding API call + a failing hybrid
 * query for nothing. We memoize a "does kg_chunks have any rows?" check per
 * process: a positive result is sticky for the instance lifetime; a negative is
 * re-probed on a short TTL, so retrieval stays a true no-op until ingestion
 * lands and then auto-enables within one TTL — no redeploy needed.
 */
const READY_TTL_MS = 5 * 60 * 1000;
let readyCache: boolean | null = null;
let readyCheckedAt = 0;

async function ragCorpusReady(): Promise<boolean> {
  if (!sql) return false;
  if (readyCache === true) return true;
  const now = Date.now();
  if (readyCache === false && now - readyCheckedAt < READY_TTL_MS) return false;
  try {
    const rows = (await sql`SELECT 1 AS ok FROM kg_chunks LIMIT 1`) as Array<{ ok: number }>;
    readyCache = rows.length > 0;
  } catch {
    // Table missing / not migrated yet → treat as not ready (no log spam).
    readyCache = false;
  }
  readyCheckedAt = now;
  return readyCache;
}

/** Test-only: reset the memoized readiness probe. */
export function resetRagReadyCache(): void {
  readyCache = null;
  readyCheckedAt = 0;
}

/** Retrieve the most relevant authored chunks for a query. Never throws. */
export async function retrieveChunks(opts: RetrieveOptions): Promise<RagChunk[]> {
  const query = (opts.query ?? '').trim();
  if (!sql || !query) return [];
  // Skip all work (incl. the embedding call) until the corpus is actually present.
  if (!(await ragCorpusReady())) return [];
  const lang = opts.lang ?? detectLang(query);
  const topK = opts.topK ?? DEFAULT_TOP_K;
  const candK = opts.candidateK ?? DEFAULT_CANDIDATE_K;
  const subject = opts.subject ?? null;

  try {
    const vec = await embedQuery(query);
    const vecStr = vec ? `[${vec.join(',')}]` : null;
    if (vecStr) {
      const rows = (await sql`
        WITH dense AS (
          SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> ${vecStr}::vector) AS rnk
          FROM kg_chunks
          WHERE lang = ${lang}
            AND embedding IS NOT NULL
            AND (${subject}::text IS NULL OR provenance->>'subject' = ${subject})
          ORDER BY embedding <=> ${vecStr}::vector
          LIMIT ${candK}
        ),
        lex AS (
          SELECT id, ROW_NUMBER() OVER (
                   ORDER BY ts_rank(tsv, websearch_to_tsquery('simple', ${query})) DESC
                 ) AS rnk
          FROM kg_chunks
          WHERE lang = ${lang}
            AND tsv @@ websearch_to_tsquery('simple', ${query})
            AND (${subject}::text IS NULL OR provenance->>'subject' = ${subject})
          LIMIT ${candK}
        ),
        trgm AS (
          SELECT id, ROW_NUMBER() OVER (ORDER BY word_similarity(${query}, text) DESC) AS rnk
          FROM kg_chunks
          WHERE lang = ${lang}
            AND (${subject}::text IS NULL OR provenance->>'subject' = ${subject})
            AND word_similarity(${query}, text) > 0.1
          ORDER BY word_similarity(${query}, text) DESC
          LIMIT ${candK}
        ),
        fused AS (
          SELECT id,
                 SUM(w) AS score
          FROM (
            SELECT id, 1.0 / (${RRF_K} + rnk) AS w FROM dense
            UNION ALL
            SELECT id, 1.0 / (${RRF_K} + rnk) AS w FROM lex
            UNION ALL
            SELECT id, 1.0 / (${RRF_K} + rnk) AS w FROM trgm
          ) u
          GROUP BY id
        )
        SELECT k.id, k.text, k.heading, k.source_type, k.source_doc_id, k.concept_id,
               k.provenance->>'title' AS title, f.score
        FROM fused f JOIN kg_chunks k ON k.id = f.id
        ORDER BY f.score DESC
        LIMIT ${topK}
      `) as Row[];
      return rows.map((r) => toChunk(r, 'hybrid'));
    }

    // Lexical-only fallback (embedding API unavailable): fuse FTS + trigram via
    // RRF so Hebrew (morphology-heavy) still retrieves usefully without dense.
    logger.warn('rag-retrieve: embedding unavailable, using lexical-only');
    const rows = (await sql`
      WITH lex AS (
        SELECT id, ROW_NUMBER() OVER (
                 ORDER BY ts_rank(tsv, websearch_to_tsquery('simple', ${query})) DESC
               ) AS rnk
        FROM kg_chunks
        WHERE lang = ${lang}
          AND tsv @@ websearch_to_tsquery('simple', ${query})
          AND (${subject}::text IS NULL OR provenance->>'subject' = ${subject})
        LIMIT ${candK}
      ),
      trgm AS (
        SELECT id, ROW_NUMBER() OVER (ORDER BY word_similarity(${query}, text) DESC) AS rnk
        FROM kg_chunks
        WHERE lang = ${lang}
          AND (${subject}::text IS NULL OR provenance->>'subject' = ${subject})
          AND word_similarity(${query}, text) > 0.1
        ORDER BY word_similarity(${query}, text) DESC
        LIMIT ${candK}
      ),
      fused AS (
        SELECT id, SUM(w) AS score FROM (
          SELECT id, 1.0 / (${RRF_K} + rnk) AS w FROM lex
          UNION ALL
          SELECT id, 1.0 / (${RRF_K} + rnk) AS w FROM trgm
        ) u
        GROUP BY id
      )
      SELECT k.id, k.text, k.heading, k.source_type, k.source_doc_id, k.concept_id,
             k.provenance->>'title' AS title, f.score
      FROM fused f JOIN kg_chunks k ON k.id = f.id
      ORDER BY f.score DESC
      LIMIT ${topK}
    `) as Row[];
    return rows.map((r) => toChunk(r, 'lexical'));
  } catch (err) {
    logger.error('rag-retrieve: query failed', { err: String(err) });
    return [];
  }
}

/** Format retrieved chunks as a compact, citable context block for prompts. */
export function formatChunksForPrompt(chunks: RagChunk[], lang: RagLang): string {
  if (chunks.length === 0) return '';
  const header =
    lang === 'he'
      ? 'קטעי מקור רלוונטיים מתוך התוכן שנכתב (צטט לפי [כותרת]):'
      : 'Relevant source passages from the authored corpus (cite by [heading]):';
  const body = chunks
    .map((c, i) => {
      const label = c.heading || c.title || c.sourceDocId;
      return `[${i + 1}] (${label}) ${c.text}`;
    })
    .join('\n\n');
  return `${header}\n\n${body}`;
}
