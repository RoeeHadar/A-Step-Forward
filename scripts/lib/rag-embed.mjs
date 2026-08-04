/**
 * Embeddings for offline RAG ingestion. Mirrors apps/web/src/lib/rag-embed.ts
 * (model nvidia/nv-embedqa-e5-v5, 1024-dim, asymmetric passage/query) so ingested
 * chunk vectors are directly comparable to query vectors produced by the web app.
 *
 * Run the ingestion script with `node --use-system-ca` behind a TLS-intercepting
 * proxy (same fix used for the Neon driver).
 */
export const EMBED_MODEL = 'nvidia/nv-embedqa-e5-v5';
export const EMBED_DIM = 1024;

const MAX_INPUT_CHARS = 8000;
const DEFAULT_TIMEOUT_MS = 30000;

export function makeEmbedder({ apiKey, baseUrl } = {}) {
  const key = apiKey || process.env.NVIDIA_API_KEY;
  const url = (baseUrl || process.env.NVIDIA_BASE_URL || 'https://integrate.api.nvidia.com/v1').replace(
    /\/$/,
    '',
  );
  if (!key) throw new Error('NVIDIA_API_KEY not set (needed for embeddings)');

  async function embedBatch(texts, inputType, { retries = 3 } = {}) {
    let attempt = 0;
    for (;;) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
      try {
        const res = await fetch(`${url}/embeddings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${key}`,
          },
          body: JSON.stringify({
            model: EMBED_MODEL,
            input: texts.map((t) => String(t ?? '').slice(0, MAX_INPUT_CHARS)),
            input_type: inputType,
            encoding_format: 'float',
            truncate: 'END',
          }),
          signal: controller.signal,
        });
        if (res.status === 429 || res.status >= 500) {
          throw new Error(`retryable HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);
        }
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${(await res.text()).slice(0, 300)}`);
        }
        const json = await res.json();
        const data = json.data;
        if (!Array.isArray(data) || data.length !== texts.length) {
          throw new Error(`unexpected shape: got ${data?.length} want ${texts.length}`);
        }
        const ordered = [...data].sort((a, b) => (a.index ?? 0) - (b.index ?? 0));
        const vecs = ordered.map((d) => d.embedding);
        if (vecs.some((v) => !Array.isArray(v) || v.length !== EMBED_DIM)) {
          throw new Error('bad vector length');
        }
        return vecs;
      } catch (err) {
        attempt += 1;
        if (attempt > retries) throw err;
        const backoff = Math.min(8000, 500 * 2 ** attempt);
        await new Promise((r) => setTimeout(r, backoff));
      } finally {
        clearTimeout(timer);
      }
    }
  }

  return { embedBatch, EMBED_MODEL, EMBED_DIM };
}
