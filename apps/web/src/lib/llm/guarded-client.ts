/**
 * AS-95: guarded LLM client policy for apps/web, mirroring the Python guard
 * (packages/agents/agents/base/llm.py, AS-91/92/93, ADR-0004):
 *  - LLM_PROVIDER is matched case-insensitively and only `groq` is accepted;
 *  - manifest-style ids are mapped onto Groq ids, Groq ids pass through,
 *    anything else throws before any request is made;
 *  - failover to the next model happens only on retriable failures
 *    (timeout, network, 429, 5xx) — never on 400/401/403 or other 4xx;
 *  - max_tokens uses `??`, so an explicit 0 is kept.
 *
 * Every apps/web LLM request goes through `llm-provider.ts`, which calls
 * `guardModelChain` before its first fetch and `shouldFailover*` per attempt.
 * Pure module (no fetch, no env side effects) so it is unit-testable.
 */

export class LLMGuardError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'LLMGuardError';
  }
}

/** ADR-0004 model map (same entries as Python GROQ_MODEL_MAP). */
export const GROQ_MODEL_MAP: Readonly<Record<string, string>> = Object.freeze({
  'claude-opus-4-8': 'llama-3.3-70b-versatile',
  'claude-sonnet-4-5': 'llama-3.3-70b-versatile',
  'claude-haiku-4-5': 'llama-3.1-8b-instant',
  'gpt-5-mini': 'llama-3.1-8b-instant',
});

/**
 * Groq ids passed through unchanged: exactly the ADR-0004 / Python natives.
 * AS-95 r1: fail closed; any extension is proposed in AS-100.
 */
export const GROQ_NATIVE_MODELS: ReadonlySet<string> = new Set([
  'llama-3.3-70b-versatile',
  'llama-3.1-8b-instant',
]);

/** Normalise LLM_PROVIDER ('GROQ', ' Groq ', unset → 'groq'); anything else throws. */
export function resolveProvider(raw: string | undefined | null): 'groq' {
  const p = (raw ?? '').trim().toLowerCase();
  if (p === '' || p === 'groq') return 'groq';
  throw new LLMGuardError(
    `LLM_PROVIDER=${JSON.stringify(raw)} is not supported; only 'groq' is configured (ADR-0004)`,
  );
}

/** Map a model id to the Groq id that is actually sent, or throw. */
export function resolveModel(model: string, provider: string | undefined | null = 'groq'): string {
  resolveProvider(provider);
  if (GROQ_NATIVE_MODELS.has(model)) return model;
  const mapped = GROQ_MODEL_MAP[model];
  if (mapped) return mapped;
  throw new LLMGuardError(
    `model ${JSON.stringify(model)} has no Groq mapping; add it to GROQ_MODEL_MAP or use one of ${[
      ...GROQ_NATIVE_MODELS,
    ]
      .sort()
      .join(', ')}`,
  );
}

/** Resolve a whole chain up front (so a bad id throws with 0 requests); de-duplicated, order kept. */
export function guardModelChain(models: readonly string[], provider: string | undefined | null): string[] {
  resolveProvider(provider);
  return [...new Set(models.map((m) => resolveModel(m, provider)))];
}

/** Retriable HTTP status: 429 or any 5xx. 400/401/403 (and other 4xx) are not. */
export function isRetriableStatus(status: number): boolean {
  return status === 429 || (status >= 500 && status <= 599);
}

/** Retriable thrown error: abort/timeout or network-level failure. */
export function isRetriableError(err: unknown): boolean {
  const name = err instanceof Error ? err.name : '';
  const msg = String(err);
  if (name === 'AbortError' || name === 'TimeoutError' || /abort|timed? ?out/i.test(msg)) return true;
  if (err instanceof TypeError && /fetch failed|network/i.test(msg)) return true;
  return /ENOTFOUND|ECONNREFUSED|ECONNRESET|ETIMEDOUT|EAI_AGAIN|network|fetch failed|socket hang up/i.test(msg);
}

/** `??` semantics: only null/undefined fall back to the default. */
export function resolveMaxTokens(maxTokens: number | undefined | null, fallback: number): number {
  return maxTokens ?? fallback;
}
