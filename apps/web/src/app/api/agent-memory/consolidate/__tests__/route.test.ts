/**
 * AS-100: an env-set unknown model makes the real guard throw inside the
 * consolidation LLM call; the route must return a handled JSON error.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));
vi.mock('@clerk/nextjs/server', () => ({ auth: async () => ({ userId: 'user_test' }) }));
vi.mock('@/lib/neon-db', () => ({ dbConfigured: true }));
// Stand-in for the DB-bound consolidator: it makes the same cheap-tier JSON
// call through the real llm-provider + guard (persona-consolidator.ts:166).
vi.mock('@/lib/persona-consolidator', async () => {
  const { llmCompleteJson } = await import('@/lib/llm-provider');
  return {
    consolidateLearnerMemory: async () => {
      await llmCompleteJson({ messages: [{ role: 'user', content: 'notes' }], modelTier: 'cheap', jsonMode: true });
      return { ran: true };
    },
  };
});

import { POST } from '../route';
import { resetLLMConfigCache } from '@/lib/llm-provider';

const ENV = { ...process.env };
const fetchMock = vi.fn();

beforeEach(() => {
  process.env = { ...ENV };
  for (const k of ['LLM_BASE_URL', 'GROQ_BASE_URL', 'LLM_PROVIDER', 'LLM_PRIMARY_MODEL', 'LLM_FALLBACK_MODELS']) delete process.env[k];
  process.env.GROQ_API_KEY = 'placeholder-groq';
  process.env.LLM_CHEAP_MODEL = 'not-a-groq-model';
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
  resetLLMConfigCache();
});
afterEach(() => {
  vi.unstubAllGlobals();
  process.env = { ...ENV };
  resetLLMConfigCache();
});

describe('POST /api/agent-memory/consolidate (AS-100)', () => {
  it('returns a handled JSON 5xx on a guard error, with 0 fetches', async () => {
    const res = await POST(new Request('http://localhost/api/agent-memory/consolidate', { method: 'POST', body: '{}' }));
    expect(res.status).toBeGreaterThanOrEqual(400);
    expect(res.status).toBeLessThan(600);
    const body = (await res.json()) as { error?: string };
    expect(body.error).toBe('llm_misconfigured');
    expect(JSON.stringify(body)).not.toContain('not-a-groq-model');
    expect(fetchMock).toHaveBeenCalledTimes(0);
  });
});
