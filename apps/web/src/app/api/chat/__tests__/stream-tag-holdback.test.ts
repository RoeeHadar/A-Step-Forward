/**
 * AS-33 regression: a reply whose [[ASF_MEMORY_NOTE:…]] tag spans more than one
 * 48-char emit chunk must not stall the /api/chat data stream. Before the fix,
 * pull() enqueued nothing for a chunk wholly inside an open tag and was never
 * re-invoked, so the stream never closed and the turn was never persisted.
 * In-process, stub LLM, fake DB, no network.
 */
import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';

const st = vi.hoisted(() => ({
  afterJobs: [] as Promise<unknown>[],
  recordChatTurn: [] as Array<{ role: string; content: string }>,
  appendAgentNote: [] as Array<{ kind: string; content: string }>,
}));

const NOTE = 'HOLDBACK_NOTE learner moves terms across = without flipping the sign, twice';
const REPLY =
  "Let's take it one step at a time. What do you get if you move the 3 to the other side? " +
  `[[ASF_MEMORY_NOTE:${JSON.stringify({ kind: 'misconception', content: NOTE, importance: 4 })}]]`;

vi.mock('@clerk/nextjs/server', () => ({
  auth: async () => ({ userId: 'as33-user', sessionClaims: { metadata: { age: 17 } } }),
}));
vi.mock('next/headers', () => ({
  cookies: async () => ({ get: (k: string) => (k === 'asf-locale' ? { value: 'en' } : undefined) }),
}));
vi.mock('next/server', () => ({
  after: (fn: () => unknown) => {
    st.afterJobs.push(Promise.resolve().then(fn).catch(() => undefined));
  },
}));
vi.mock('@/lib/neon-db', async (importOriginal) => {
  const orig = (await importOriginal()) as Record<string, unknown>;
  const empty = (k: string): unknown =>
    /Mastery$/.test(k) ? {} : /^(fetch|list|select)|s$/.test(k) ? [] : null;
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(orig)) {
    if (typeof v !== 'function' || /^[A-Z]/.test(k)) { out[k] = v; continue; }
    out[k] = (...a: unknown[]) => {
      try {
        const r = (v as (...x: unknown[]) => unknown)(...a);
        return r instanceof Promise ? r.then((x) => x ?? empty(k), () => empty(k)) : r;
      } catch {
        return empty(k);
      }
    };
  }
  out.recordChatTurn = async (_l: string, _a: string, role: string, content: string) => {
    st.recordChatTurn.push({ role, content });
  };
  out.appendAgentNote = async (_l: string, _a: string, note: { kind: string; content: string }) => {
    st.appendAgentNote.push(note);
    return 'note-1';
  };
  return out;
});
vi.mock('@/lib/rag-retrieve', async (importOriginal) => ({
  ...((await importOriginal()) as Record<string, unknown>),
  retrieveChunks: async () => [],
}));
vi.mock('@/lib/llm-provider', async (importOriginal) => ({
  ...((await importOriginal()) as Record<string, unknown>),
  llmConfigured: () => true,
  toolCallingAvailable: () => false,
  llmStream: async function* () { yield REPLY; },
  llmComplete: async () => null,
  llmCompleteJson: async () => null,
  llmCompleteWithTools: async () => null,
}));

async function readWithTimeout(res: Response, ms: number) {
  const reader = res.body!.getReader();
  const dec = new TextDecoder();
  let raw = '';
  const deadline = Date.now() + ms;
  for (;;) {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const r = await Promise.race([
      reader.read(),
      new Promise<null>((ok) => { timer = setTimeout(() => ok(null), Math.max(0, deadline - Date.now())); }),
    ]);
    clearTimeout(timer);
    if (!r) { await reader.cancel().catch(() => undefined); return { raw, closed: false }; }
    if (r.done) return { raw, closed: true };
    raw += dec.decode(r.value, { stream: true });
  }
}

describe('/api/chat stream with a long machine tag (AS-33)', () => {
  let POST: (r: Request) => Promise<Response>;
  // AS-65: snapshot env + fetch overridden below; restored in afterAll (single-fork leak).
  const AS65_KEYS = ['DATABASE_URL', 'POSTGRES_URL', 'GROQ_API_KEY', 'LLM_API_KEY', 'LLM_BASE_URL'] as const;
  const as65Saved: Record<string, string | undefined> = {};
  let as65Fetch: typeof fetch;
  afterAll(() => {
    globalThis.fetch = as65Fetch;
    for (const k of AS65_KEYS) {
      const v = as65Saved[k];
      if (v === undefined) delete process.env[k];
      else process.env[k] = v;
    }
  });
  beforeAll(async () => {
    for (const k of AS65_KEYS) as65Saved[k] = process.env[k];
    as65Fetch = globalThis.fetch;
    for (const k of ['DATABASE_URL', 'POSTGRES_URL', 'GROQ_API_KEY', 'LLM_API_KEY']) delete process.env[k];
    process.env.LLM_API_KEY = 'placeholder-offline';
    process.env.LLM_BASE_URL = 'http://test.invalid/v1';
    globalThis.fetch = (async () => { throw new Error('network disabled in test'); }) as typeof fetch;
    POST = (await import('@/app/api/chat/route')).POST;
  }, 60_000);

  it('closes the stream, hides the tag, and persists turn + memory note', async () => {
    expect(REPLY.length - REPLY.indexOf('[[ASF_')).toBeGreaterThan(96); // spans >1 whole 48-char chunk
    const res = await POST(new Request('http://test.local/api/chat', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: 'I moved 3 over and got x=7, is that right?' }], agent: 'tutor', sessionId: 'as33-s1' }),
    }));
    expect(res.status).toBe(200);
    const { raw, closed } = await readWithTimeout(res, 3000);
    expect(closed).toBe(true);
    const text = raw.split('\n').filter((l) => l.startsWith('0:')).map((l) => JSON.parse(l.slice(2)) as string).join('');
    expect(text).toContain('one step at a time');
    expect(raw).not.toContain('ASF_');
    expect(raw).not.toContain('HOLDBACK_NOTE');
    expect(raw).toMatch(/(^|\n)d:/); // finish frame
    await Promise.all(st.afterJobs.splice(0));
    for (let i = 0; i < 20; i++) await new Promise((ok) => setImmediate(ok));
    expect(st.recordChatTurn.some((t) => t.role === 'assistant')).toBe(true);
    expect(st.recordChatTurn.find((t) => t.role === 'assistant')!.content).not.toContain('ASF_');
    expect(st.appendAgentNote).toEqual([expect.objectContaining({ kind: 'misconception', content: NOTE })]);
  }, 30_000);
});
