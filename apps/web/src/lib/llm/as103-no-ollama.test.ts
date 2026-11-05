/**
 * AS-103: after removing the ollama/local branches, LLM_PROVIDER=ollama or an
 * unknown provider and local/ollama base URLs still fail closed with the same
 * guard errors and 0 requests; Groq path still reachable. Fake fetch only.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));

import { llmComplete, llmCompleteJson, llmCompleteWithTools, llmStream, resetLLMConfigCache } from '@/lib/llm-provider';

const fetchMock = vi.fn();
const ENV = { ...process.env };
const msgs = [{ role: 'user' as const, content: 'q' }];
const TOOLS = [{ type: 'function' as const, function: { name: 'lookup', description: 'd', parameters: { type: 'object' } } }];

function ok(_url: string, init: RequestInit) {
  const body = JSON.parse(String(init.body)) as { stream?: boolean };
  if (body.stream) {
    const enc = new TextEncoder();
    return new Response(
      new ReadableStream<Uint8Array>({
        start(c) {
          c.enqueue(enc.encode(`data: ${JSON.stringify({ choices: [{ delta: { content: 'ok' } }] })}\n\n`));
          c.enqueue(enc.encode('data: [DONE]\n\n'));
          c.close();
        },
      }),
      { status: 200 },
    );
  }
  return new Response(JSON.stringify({ choices: [{ message: { content: 'ok' } }] }), { status: 200 });
}

beforeEach(() => {
  process.env = { ...ENV };
  for (const k of ['LLM_PROVIDER', 'LLM_BASE_URL', 'GROQ_BASE_URL', 'LLM_API_KEY', 'LLM_PRIMARY_MODEL', 'LLM_CHEAP_MODEL', 'LLM_FALLBACK_MODELS', 'CHAT_MODEL_POLICY', 'ALLOW_REAL_LLM', 'EVAL_REAL']) delete process.env[k];
  process.env.GROQ_API_KEY = 'placeholder-groq';
  fetchMock.mockReset();
  fetchMock.mockImplementation(async (u: string, i: RequestInit) => ok(u, i));
  vi.stubGlobal('fetch', fetchMock);
  resetLLMConfigCache();
});
afterEach(() => {
  vi.unstubAllGlobals();
  process.env = { ...ENV };
  resetLLMConfigCache();
});

async function drain(it: AsyncGenerator<string>) {
  for await (const _ of it) void _;
}

async function allFour(): Promise<string[]> {
  const out: string[] = [];
  const grab = async (p: Promise<unknown>) => {
    try { await p; out.push('resolved'); } catch (e) { out.push((e as Error).name + ': ' + (e as Error).message); }
  };
  await grab(llmComplete({ messages: msgs }));
  await grab(drain(llmStream({ messages: msgs })));
  await grab(llmCompleteWithTools({ messages: msgs, tools: TOOLS }));
  await grab(llmCompleteJson({ messages: msgs }));
  return out;
}

describe('AS-103: provider guard unchanged', () => {
  for (const p of ['ollama', 'OLLAMA', 'local', 'bogus-provider']) {
    it(`LLM_PROVIDER=${p} fails closed with the AS-100 guard error, 0 fetches`, async () => {
      process.env.LLM_PROVIDER = p;
      resetLLMConfigCache();
      const errs = await allFour();
      const want = `LLMGuardError: LLM_PROVIDER=${JSON.stringify(p)} is not supported; only 'groq' is configured (ADR-0004)`;
      expect(errs).toEqual([want, want, want, want]);
      expect(fetchMock).toHaveBeenCalledTimes(0);
    });
  }

  for (const url of ['http://localhost:11434/v1', 'http://127.0.0.1:11434/v1', 'http://ollama:11434/v1']) {
    it(`LLM_BASE_URL=${url} (keyed or keyless) throws the base URL guard, 0 fetches`, async () => {
      process.env.LLM_BASE_URL = url;
      for (const keyed of [true, false]) {
        if (keyed) process.env.GROQ_API_KEY = 'placeholder-groq';
        else delete process.env.GROQ_API_KEY;
        resetLLMConfigCache();
        const errs = await allFour();
        for (const e of errs) expect(e).toMatch(/^LLMGuardError: .*base URL/);
      }
      expect(fetchMock).toHaveBeenCalledTimes(0);
    });
  }

  it('no key + default Groq URL: not configured, returns null/empty, 0 fetches', async () => {
    delete process.env.GROQ_API_KEY;
    resetLLMConfigCache();
    expect(await llmComplete({ messages: msgs })).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(0);
  });

  it('Groq key + default URL: all four entrypoints reach the Groq endpoint', async () => {
    const errs = await allFour();
    expect(errs).toEqual(['resolved', 'resolved', 'resolved', 'resolved']);
    expect(fetchMock.mock.calls.length).toBeGreaterThanOrEqual(4);
    for (const [u] of fetchMock.mock.calls) expect(String(u).startsWith('https://api.groq.com/openai/v1/')).toBe(true);
  });
});
