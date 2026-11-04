/**
 * AS-100: LLM_BASE_URL / GROQ_BASE_URL other than the Groq endpoint throws
 * before any request (complete, stream, tools). Fake fetch only.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));

import { llmComplete, llmCompleteWithTools, llmStream, resetLLMConfigCache } from '@/lib/llm-provider';

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

const BAD = [
  ['LLM_BASE_URL', 'https://integrate.api.nvidia.com/v1'],
  ['LLM_BASE_URL', 'http://localhost:11434/v1'],
  ['LLM_BASE_URL', 'http://api.groq.com/openai/v1'],
  ['LLM_BASE_URL', 'https://api.groq.com.evil.example/openai/v1'],
  ['LLM_BASE_URL', 'https://api.groq.com/openai/v2'],
  ['GROQ_BASE_URL', 'https://api.together.xyz/v1'],
] as const;

async function drain(it: AsyncGenerator<string>) {
  for await (const _ of it) void _;
}

describe('AS-100: non-Groq base URL throws with 0 requests', () => {
  for (const [name, url] of BAD) {
    it(`${name}=${url}: complete, stream and tools all throw, 0 fetches`, async () => {
      process.env[name] = url;
      resetLLMConfigCache();
      await expect(llmComplete({ messages: msgs })).rejects.toThrow(/base URL/);
      await expect(drain(llmStream({ messages: msgs }))).rejects.toThrow(/base URL/);
      await expect(llmCompleteWithTools({ messages: msgs, tools: TOOLS })).rejects.toThrow(/base URL/);
      expect(fetchMock).toHaveBeenCalledTimes(0);
    });
  }

  for (const url of ['https://api.groq.com/openai/v1', 'https://api.groq.com/openai/v1/', ' "https://api.groq.com/openai/v1/" ']) {
    it(`accepts the canonical Groq URL ${JSON.stringify(url)}`, async () => {
      process.env.LLM_BASE_URL = url;
      process.env.GROQ_BASE_URL = url;
      resetLLMConfigCache();
      await llmComplete({ messages: msgs });
      await drain(llmStream({ messages: msgs }));
      await llmCompleteWithTools({ messages: msgs, tools: TOOLS });
      expect(fetchMock.mock.calls.length).toBe(3);
      for (const [u] of fetchMock.mock.calls) expect(u).toBe('https://api.groq.com/openai/v1/chat/completions');
    });
  }
});
