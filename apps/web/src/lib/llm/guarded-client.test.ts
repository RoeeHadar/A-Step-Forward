/**
 * AS-95: every apps/web LLM request goes through the guarded client.
 * Fake fetch only (vi.stubGlobal) — no network, placeholder env, no keys.
 * Call sites covered: llmComplete, llmCompleteJson, llmStream, llmCompleteWithTools
 * (the only fetch site, fetchCompletions, sits under these), the chat route's
 * stream→complete pattern, concept-resolver (classifier) and react-loop (tools).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));

import {
  llmComplete,
  llmCompleteJson,
  llmCompleteWithTools,
  llmStream,
  resetLLMConfigCache,
  resolveChatModelChain,
  resolveClassifierModelChain,
} from '@/lib/llm-provider';

const fetchMock = vi.fn();
const ENV = { ...process.env };

function okJson(content = 'ok') {
  return new Response(JSON.stringify({ choices: [{ message: { content } }] }), { status: 200 });
}
function okTools() {
  return new Response(
    JSON.stringify({
      choices: [{ message: { content: '', tool_calls: [{ id: 'c1', type: 'function', function: { name: 'lookup', arguments: '{}' } }] }, finish_reason: 'tool_calls' }],
    }),
    { status: 200 },
  );
}
function okStream(tokens: string[]) {
  const enc = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      for (const t of tokens) c.enqueue(enc.encode(`data: ${JSON.stringify({ choices: [{ delta: { content: t } }] })}\n\n`));
      c.enqueue(enc.encode('data: [DONE]\n\n'));
      c.close();
    },
  });
  return new Response(body, { status: 200, headers: { 'content-type': 'text/event-stream' } });
}
function status(code: number) {
  return new Response(JSON.stringify({ error: { message: `http ${code}` } }), { status: code });
}
const sentModels = () => fetchMock.mock.calls.map((c) => JSON.parse(String((c[1] as RequestInit).body)).model as string);
const sentBody = (i = 0) => JSON.parse(String((fetchMock.mock.calls[i]![1] as RequestInit).body)) as Record<string, unknown>;
const msgs = [{ role: 'user' as const, content: 'q' }];
const TOOLS = [{ type: 'function' as const, function: { name: 'lookup', description: 'd', parameters: { type: 'object' } } }];

async function drain(it: AsyncGenerator<string>): Promise<string> {
  let out = '';
  for await (const t of it) out += t;
  return out;
}

beforeEach(() => {
  process.env = { ...ENV };
  process.env.LLM_API_KEY = 'placeholder-offline';
  process.env.LLM_BASE_URL = 'http://test.invalid/v1';
  for (const k of ['LLM_PROVIDER', 'GROQ_API_KEY', 'LLM_PRIMARY_MODEL', 'LLM_CHEAP_MODEL', 'LLM_FALLBACK_MODELS', 'CHAT_MODEL_POLICY', 'NVIDIA_API_KEY', 'NVIDIA_FALLBACK_MODELS', 'ALLOW_REAL_LLM', 'EVAL_REAL']) delete process.env[k];
  resetLLMConfigCache();
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(() => {
  vi.unstubAllGlobals();
  process.env = { ...ENV };
  resetLLMConfigCache();
});

describe('model map (ADR-0004) at every call site', () => {
  it('llmComplete sends mapped Groq ids', async () => {
    fetchMock.mockResolvedValueOnce(okJson());
    await llmComplete({ messages: msgs, models: ['claude-sonnet-4-5'] });
    expect(sentModels()).toEqual(['llama-3.3-70b-versatile']);
  });
  it('maps opus/sonnet → 70b and haiku/gpt-5-mini → 8b, Groq ids pass through', async () => {
    fetchMock.mockImplementation(async () => okJson());
    for (const [m, want] of [
      ['claude-opus-4-8', 'llama-3.3-70b-versatile'],
      ['claude-sonnet-4-5', 'llama-3.3-70b-versatile'],
      ['claude-haiku-4-5', 'llama-3.1-8b-instant'],
      ['gpt-5-mini', 'llama-3.1-8b-instant'],
      ['llama-3.1-8b-instant', 'llama-3.1-8b-instant'],
    ] as const) {
      fetchMock.mockClear();
      await llmComplete({ messages: msgs, models: [m] });
      expect(sentModels()).toEqual([want]);
    }
  });
  it('llmCompleteJson sends a mapped id', async () => {
    fetchMock.mockResolvedValueOnce(okJson('{"a":1}'));
    const r = await llmCompleteJson<{ a: number }>({ messages: msgs, models: ['gpt-5-mini'] });
    expect(r?.json.a).toBe(1);
    expect(sentModels()).toEqual(['llama-3.1-8b-instant']);
  });
  it('llmStream sends a mapped id and streams tokens intact', async () => {
    fetchMock.mockResolvedValueOnce(okStream(['שלום', ' ', 'world']));
    expect(await drain(llmStream({ messages: msgs, models: ['claude-opus-4-8'] }))).toBe('שלום world');
    expect(sentModels()).toEqual(['llama-3.3-70b-versatile']);
    expect(sentBody().stream).toBe(true);
  });
  it('llmCompleteWithTools maps before the tool-capable filter', async () => {
    fetchMock.mockResolvedValueOnce(okTools());
    const r = await llmCompleteWithTools({ messages: msgs, tools: TOOLS, models: ['claude-sonnet-4-5'] });
    expect(r?.toolCalls[0]?.function.name).toBe('lookup');
    expect(sentModels()).toEqual(['llama-3.3-70b-versatile']);
  });
  it('chat route pattern (resolveChatModelChain → llmStream, llmComplete backup) uses only Groq ids', async () => {
    process.env.LLM_PRIMARY_MODEL = 'claude-sonnet-4-5';
    process.env.LLM_CHEAP_MODEL = 'claude-haiku-4-5';
    process.env.NVIDIA_API_KEY = 'placeholder-offline';
    process.env.NVIDIA_FALLBACK_MODELS = 'meta/llama-3.3-70b-instruct';
    resetLLMConfigCache();
    fetchMock.mockResolvedValueOnce(okStream([])).mockImplementation(async () => okJson('backup'));
    const opts = { messages: msgs, models: resolveChatModelChain() };
    const streamed = await drain(llmStream(opts));
    const backup = streamed.trim() ? null : await llmComplete(opts);
    expect(backup?.content).toBe('backup');
    for (const m of sentModels()) expect(['llama-3.3-70b-versatile', 'llama-3.1-8b-instant']).toContain(m);
    expect(sentModels()).not.toContain('meta/llama-3.3-70b-instruct');
  });
  it('concept-resolver classifier call sends a mapped cheap id', async () => {
    process.env.LLM_CHEAP_MODEL = 'claude-haiku-4-5';
    resetLLMConfigCache();
    fetchMock.mockImplementation(async () => okJson('{"ids":[]}'));
    const { resolveConceptsWithClassifier } = await import('@/lib/concept-resolver');
    await resolveConceptsWithClassifier('zxqv wplk mrtg bnfh qqzz', []);
    expect(resolveClassifierModelChain()[0]).toBe('claude-haiku-4-5');
    expect(fetchMock.mock.calls.length).toBeGreaterThan(0);
    expect(sentModels().every((m) => m === 'llama-3.1-8b-instant')).toBe(true);
  });
  it('react-loop planner call sends a mapped tool-capable id', async () => {
    process.env.LLM_PRIMARY_MODEL = 'claude-sonnet-4-5';
    process.env.LLM_FALLBACK_MODELS = 'claude-sonnet-4-5';
    resetLLMConfigCache();
    fetchMock.mockImplementation(async () => okJson('final'));
    const { runReactLoop } = await import('@/lib/react-loop');
    await runReactLoop({
      system: 's', memory: [], userMessage: 'q', ctx: { userId: 'u', agent: 'tutor', locale: 'en' },
      tools: [{ spec: TOOLS[0]!, handler: async () => 'obs' }] as never,
    });
    expect(sentModels()).toEqual(['llama-3.3-70b-versatile']);
  });
});

describe('unknown provider / model throws with 0 fetch calls', () => {
  const calls = {
    llmComplete: (models?: string[]) => llmComplete({ messages: msgs, models }),
    llmCompleteJson: (models?: string[]) => llmCompleteJson({ messages: msgs, models }),
    llmStream: (models?: string[]) => drain(llmStream({ messages: msgs, models })),
    llmCompleteWithTools: (models?: string[]) => llmCompleteWithTools({ messages: msgs, tools: TOOLS, models }),
  };
  for (const [name, call] of Object.entries(calls)) {
    it(`${name}: unknown model`, async () => {
      await expect(call(['llama-3.3-70b-versatile', 'some-unknown-model'])).rejects.toThrow(/no Groq mapping/);
      expect(fetchMock).toHaveBeenCalledTimes(0);
    });
    it(`${name}: LLM_PROVIDER=openai`, async () => {
      process.env.LLM_PROVIDER = 'openai';
      resetLLMConfigCache();
      await expect(call(['llama-3.3-70b-versatile'])).rejects.toThrow(/LLM_PROVIDER/);
      expect(fetchMock).toHaveBeenCalledTimes(0);
    });
  }
  it.each(['GROQ', ' Groq ', 'groq'])('LLM_PROVIDER=%j is accepted (case-insensitive)', async (p) => {
    process.env.LLM_PROVIDER = p;
    resetLLMConfigCache();
    fetchMock.mockResolvedValueOnce(okJson());
    expect((await llmComplete({ messages: msgs, models: ['gpt-5-mini'] }))?.content).toBe('ok');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe('failover only on retriable errors', () => {
  const chain = ['claude-sonnet-4-5', 'gpt-5-mini'];
  const two = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];

  it.each([500, 502, 503])('HTTP %i fails over (complete)', async (code) => {
    fetchMock.mockResolvedValueOnce(status(code)).mockResolvedValueOnce(okJson());
    expect((await llmComplete({ messages: msgs, models: chain }))?.content).toBe('ok');
    expect(sentModels()).toEqual(two);
  });
  it('HTTP 429 fails over after in-call retries (complete)', async () => {
    fetchMock.mockResolvedValueOnce(status(429)).mockResolvedValueOnce(status(429)).mockResolvedValueOnce(status(429)).mockResolvedValueOnce(okJson());
    expect((await llmComplete({ messages: msgs, models: chain }))?.content).toBe('ok');
    expect(sentModels().at(-1)).toBe('llama-3.1-8b-instant');
  }, 20_000);
  it.each([
    ['timeout', () => Object.assign(new Error('The operation was aborted'), { name: 'AbortError' })],
    ['network', () => new TypeError('fetch failed')],
  ])('%s error fails over (complete)', async (_k, mk) => {
    fetchMock.mockRejectedValueOnce(mk()).mockRejectedValueOnce(mk()).mockRejectedValueOnce(mk()).mockResolvedValueOnce(okJson());
    expect((await llmComplete({ messages: msgs, models: chain }))?.content).toBe('ok');
    expect(sentModels().at(-1)).toBe('llama-3.1-8b-instant');
  }, 20_000);
  it.each([400, 401, 403])('HTTP %i does NOT fail over (complete)', async (code) => {
    fetchMock.mockResolvedValueOnce(status(code)).mockImplementation(async () => okJson());
    expect(await llmComplete({ messages: msgs, models: chain })).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it.each([400, 401, 403])('HTTP %i does NOT fail over (stream)', async (code) => {
    fetchMock.mockResolvedValueOnce(status(code)).mockImplementation(async () => okStream(['x']));
    expect(await drain(llmStream({ messages: msgs, models: chain }))).toBe('');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it('HTTP 503 fails over (stream)', async () => {
    fetchMock.mockResolvedValueOnce(status(503)).mockResolvedValueOnce(okStream(['ok']));
    expect(await drain(llmStream({ messages: msgs, models: chain }))).toBe('ok');
    expect(sentModels()).toEqual(two);
  });
  it.each([400, 401, 403])('HTTP %i does NOT fail over (tools)', async (code) => {
    fetchMock.mockResolvedValueOnce(status(code)).mockImplementation(async () => okTools());
    expect(await llmCompleteWithTools({ messages: msgs, tools: TOOLS, models: ['claude-sonnet-4-5', 'claude-opus-4-8'] })).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe('max_tokens uses ??', () => {
  it('maxTokens=0 is sent as 0 (complete, stream, tools)', async () => {
    fetchMock.mockResolvedValueOnce(okJson()).mockResolvedValueOnce(okStream(['x'])).mockResolvedValueOnce(okTools());
    await llmComplete({ messages: msgs, models: ['gpt-5-mini'], maxTokens: 0 });
    await drain(llmStream({ messages: msgs, models: ['gpt-5-mini'], maxTokens: 0 }));
    await llmCompleteWithTools({ messages: msgs, tools: TOOLS, models: ['claude-sonnet-4-5'], maxTokens: 0 });
    expect([0, 1, 2].map((i) => sentBody(i).max_tokens)).toEqual([0, 0, 0]);
  });
  it('undefined maxTokens keeps the defaults (2048 / 1024)', async () => {
    fetchMock.mockResolvedValueOnce(okJson()).mockResolvedValueOnce(okStream(['x']));
    await llmComplete({ messages: msgs, models: ['gpt-5-mini'] });
    await drain(llmStream({ messages: msgs, models: ['gpt-5-mini'] }));
    expect([sentBody(0).max_tokens, sentBody(1).max_tokens]).toEqual([2048, 1024]);
  });
});

// AS-95 r1 — P1-1: no failover / retry once a byte reached the caller.
function streamThenThrow(tokens: string[], err: Error) {
  const enc = new TextEncoder();
  let i = 0;
  const body = new ReadableStream<Uint8Array>({
    pull(c) {
      if (i < tokens.length) {
        c.enqueue(enc.encode(`data: ${JSON.stringify({ choices: [{ delta: { content: tokens[i++] } }] })}\n\n`));
      } else {
        c.error(err);
      }
    },
  });
  return new Response(body, { status: 200, headers: { 'content-type': 'text/event-stream' } });
}

describe('r1 P1-1: stream error after the first byte re-throws, never fails over', () => {
  const chain = ['claude-sonnet-4-5', 'gpt-5-mini'];
  it.each([
    ['TypeError fetch failed', () => new TypeError('fetch failed')],
    ['AbortError', () => Object.assign(new Error('The operation was aborted'), { name: 'AbortError' })],
  ])('%s after "AB": caller gets "AB" then the error, 1 fetch, no repeated text', async (_k, mk) => {
    const err = mk();
    fetchMock.mockImplementation(async () => streamThenThrow(['A', 'B'], err));
    let got = '';
    let thrown: unknown = null;
    try {
      for await (const t of llmStream({ messages: msgs, models: chain })) got += t;
    } catch (e) {
      thrown = e;
    }
    expect(got).toBe('AB');
    expect(thrown).toBe(err);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it('error before the first byte still fails over (unchanged)', async () => {
    fetchMock
      .mockImplementationOnce(async () => streamThenThrow([], new TypeError('fetch failed')))
      .mockImplementationOnce(async () => okStream(['ok']));
    expect(await drain(llmStream({ messages: msgs, models: chain }))).toBe('ok');
    expect(sentModels()).toEqual(['llama-3.3-70b-versatile', 'llama-3.1-8b-instant']);
  });
});

// AS-95 r1 — P1-2 option (a): chain = ADR-0004 ids only, fail closed.
describe('r1 P1-2: default chain is exactly the ADR-0004 ids', () => {
  it('resolveChatModelChain() equals [llama-3.3-70b-versatile, llama-3.1-8b-instant]', () => {
    expect(resolveChatModelChain()).toEqual(['llama-3.3-70b-versatile', 'llama-3.1-8b-instant']);
  });
  it('non-ADR Groq ids are not passed through (throw, 0 fetch)', async () => {
    for (const m of ['openai/gpt-oss-120b', 'qwen/qwen3.6-27b']) {
      await expect(llmComplete({ messages: msgs, models: [m] })).rejects.toThrow(/no Groq mapping/);
    }
    expect(fetchMock).toHaveBeenCalledTimes(0);
  });
});
