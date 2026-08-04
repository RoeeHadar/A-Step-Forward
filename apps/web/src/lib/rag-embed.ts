/**
 * Text embeddings for RAG retrieval (query-time) via a hosted, stateless API.
 *
 * Model: `nvidia/nv-embedqa-e5-v5` (NVIDIA NIM) — multilingual E5, 1024-dim,
 * asymmetric: pass `input_type: 'query'` for user turns and `'passage'` for
 * ingested chunks. Using a hosted API (not in-process Transformers.js) keeps the
 * Vercel function small and cold-start-fast, and guarantees the query embedding
 * uses the SAME model as ingestion.
 *
 * All functions return `null` on any failure so callers can degrade gracefully
 * to the lexical retrieval channel instead of throwing.
 */
import 'server-only';
import { logger } from '@/lib/logger';

export const EMBED_MODEL = 'nvidia/nv-embedqa-e5-v5';
export const EMBED_DIM = 1024;

/** Max chars per input we send; the API also truncates, this bounds payload. */
const MAX_INPUT_CHARS = 8000;
/** NVIDIA embeddings accept batches; keep them modest for latency + limits. */
const MAX_BATCH = 32;
const DEFAULT_TIMEOUT_MS = 15000;

function embedConfig(): { baseUrl: string; apiKey: string } | null {
  const apiKey = process.env.NVIDIA_API_KEY;
  if (!apiKey) return null;
  const baseUrl = (process.env.NVIDIA_BASE_URL || 'https://integrate.api.nvidia.com/v1').replace(
    /\/$/,
    '',
  );
  return { baseUrl, apiKey };
}

export function embeddingsConfigured(): boolean {
  return embedConfig() !== null;
}

async function embedBatch(
  texts: string[],
  inputType: 'query' | 'passage',
  cfg: { baseUrl: string; apiKey: string },
): Promise<number[][] | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  try {
    const res = await fetch(`${cfg.baseUrl}/embeddings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${cfg.apiKey}`,
      },
      body: JSON.stringify({
        model: EMBED_MODEL,
        input: texts.map((t) => t.slice(0, MAX_INPUT_CHARS)),
        input_type: inputType,
        encoding_format: 'float',
        truncate: 'END',
      }),
      signal: controller.signal,
    });
    if (!res.ok) {
      logger.warn('rag-embed: non-ok response', { status: res.status });
      return null;
    }
    const json = (await res.json()) as { data?: Array<{ embedding?: number[]; index?: number }> };
    const data = json.data;
    if (!Array.isArray(data) || data.length !== texts.length) {
      logger.warn('rag-embed: unexpected shape', { got: data?.length, want: texts.length });
      return null;
    }
    // API preserves order but sort by index defensively.
    const ordered = [...data].sort((a, b) => (a.index ?? 0) - (b.index ?? 0));
    const out = ordered.map((d) => d.embedding);
    if (out.some((e) => !Array.isArray(e) || e.length !== EMBED_DIM)) {
      logger.warn('rag-embed: bad vector length');
      return null;
    }
    return out as number[][];
  } catch (err) {
    logger.warn('rag-embed: request failed', { err: String(err) });
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/** Embed many texts. Returns null if the batch cannot be embedded. */
export async function embedTexts(
  texts: string[],
  inputType: 'query' | 'passage',
): Promise<number[][] | null> {
  const cfg = embedConfig();
  if (!cfg) return null;
  const clean = texts.map((t) => (t ?? '').trim()).filter(() => true);
  const out: number[][] = [];
  for (let i = 0; i < clean.length; i += MAX_BATCH) {
    const batch = clean.slice(i, i + MAX_BATCH);
    const vecs = await embedBatch(batch, inputType, cfg);
    if (!vecs) return null;
    out.push(...vecs);
  }
  return out;
}

/** Embed a single user query. Returns null on failure (caller uses lexical-only). */
export async function embedQuery(text: string): Promise<number[] | null> {
  if (!text?.trim()) return null;
  const res = await embedTexts([text], 'query');
  return res?.[0] ?? null;
}
