/**
 * AS-101: no env var can route chat off Groq. NVIDIA is used only by
 * rag-embed (search embeddings). Fake fetch only — no network, placeholder keys.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));

import {
  llmComplete,
  llmCompleteJson,
  llmCompleteWithTools,
  llmStream,
  resetLLMConfigCache,
} from '@/lib/llm-provider';

const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_IDS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];
const fetchMock = vi.fn();
const ENV = { ...process.env };
const msgs = [{ role: 'user' as const, content: 'q' }];
const TOOLS = [{ type: 'function' as const, function: { name: 'lookup', description: 'd', parameters: { type: 'object' } } }];

function reply(url: string, init: RequestInit) {
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
  void url;
  return new Response(JSON.stringify({ choices: [{ message: { content: '{"ok":1}' } }] }), { status: 200 });
}

/** Every env var that could plausibly move chat to NVIDIA. */
function nvidiaEnv(primary: string) {
  process.env.GROQ_API_KEY = 'placeholder-groq';
  process.env.LLM_PRIMARY_MODEL = primary;
  process.env.LLM_CHEAP_MODEL = primary;
  process.env.LLM_FALLBACK_MODELS = primary;
  process.env.NVIDIA_API_KEY = 'placeholder-nvidia';
  process.env.NVIDIA_BASE_URL = 'https://nvidia.invalid/v1';
  process.env.NVIDIA_FALLBACK_MODELS =
    'llama-3.3-70b-versatile,llama-3.1-8b-instant,meta/llama-3.3-70b-instruct';
  resetLLMConfigCache();
}

function expectAllGroq() {
  expect(fetchMock.mock.calls.length).toBeGreaterThan(0);
  for (const [url, init] of fetchMock.mock.calls as [string, RequestInit][]) {
    expect(url).toBe(GROQ_URL);
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer placeholder-groq');
    expect(GROQ_IDS).toContain(JSON.parse(String(init.body)).model);
  }
}

beforeEach(() => {
  process.env = { ...ENV };
  for (const k of ['LLM_PROVIDER', 'LLM_BASE_URL', 'GROQ_BASE_URL', 'LLM_API_KEY', 'CHAT_MODEL_POLICY', 'ALLOW_REAL_LLM', 'EVAL_REAL']) delete process.env[k];
  fetchMock.mockReset();
  fetchMock.mockImplementation(async (url: string, init: RequestInit) => reply(url, init));
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(() => {
  vi.unstubAllGlobals();
  process.env = { ...ENV };
  resetLLMConfigCache();
});

describe('AS-101: NVIDIA_* env cannot route chat off Groq', () => {
  it('llmComplete → Groq URL + Groq id', async () => {
    nvidiaEnv('llama-3.1-8b-instant');
    await llmComplete({ messages: msgs, models: ['claude-opus-4-8'] });
    expectAllGroq();
  });
  it('llmCompleteJson → Groq URL + Groq id', async () => {
    nvidiaEnv('llama-3.1-8b-instant');
    await llmCompleteJson({ messages: msgs, models: ['claude-sonnet-4-5'] });
    expectAllGroq();
  });
  it('llmStream → Groq URL + Groq id', async () => {
    nvidiaEnv('llama-3.3-70b-versatile');
    for await (const _ of llmStream({ messages: msgs, models: ['gpt-5-mini'] })) void _;
    expectAllGroq();
  });
  it('llmCompleteWithTools → Groq URL + Groq id', async () => {
    nvidiaEnv('llama-3.1-8b-instant');
    await llmCompleteWithTools({ messages: msgs, tools: TOOLS, models: ['claude-sonnet-4-5'] });
    expectAllGroq();
  });
  it('default chains (no models option) → Groq URL + Groq ids', async () => {
    nvidiaEnv('llama-3.3-70b-versatile');
    await llmComplete({ messages: msgs });
    for await (const _ of llmStream({ messages: msgs })) void _;
    await llmCompleteWithTools({ messages: msgs, tools: TOOLS });
    expectAllGroq();
  });
  it('an NVIDIA model id from env or caller throws with 0 fetches', async () => {
    nvidiaEnv('llama-3.3-70b-versatile');
    await expect(llmComplete({ messages: msgs, models: ['meta/llama-3.3-70b-instruct'] })).rejects.toThrow(/no Groq mapping/);
    expect(fetchMock).toHaveBeenCalledTimes(0);
  });
  it('NVIDIA_BASE_URL never becomes the chat base URL (LLM_BASE_URL itself is AS-100)', async () => {
    nvidiaEnv('llama-3.3-70b-versatile');
    const { getLLMConfig } = await import('@/lib/llm-provider');
    expect(getLLMConfig().baseUrl).toBe('https://api.groq.com/openai/v1');
  });
});
