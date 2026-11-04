import http from 'node:http';
import https from 'node:https';
import fs from 'node:fs';
import path from 'node:path';
import { describe, expect, it, vi } from 'vitest';
import {
  hostsFromProviderSource,
  isLlmHost,
  LLM_HOSTS,
  restoreEnv,
  snapshotEnv,
} from './vitest-guard';

describe('AS-67 restoreEnv', () => {
  it('deletes added keys and resets changed keys in place', () => {
    const env = { KEEP: 'a', CHANGE: 'b', DROP: 'c' } as unknown as NodeJS.ProcessEnv;
    const ref = env;
    const snap = snapshotEnv(env);
    env.CHANGE = 'x';
    env.ADDED = 'y';
    delete env.DROP;
    restoreEnv(snap, env);
    expect(env).toBe(ref);
    expect(env).toEqual({ KEEP: 'a', CHANGE: 'b', DROP: 'c' });
  });
});

describe('AS-67 real-LLM block', () => {
  it('derives hosts from llm-provider.ts', () => {
    const src = fs.readFileSync(path.resolve(__dirname, '../lib/llm-provider.ts'), 'utf8');
    const derived = hostsFromProviderSource(src);
    expect(derived).toEqual(expect.arrayContaining(['api.groq.com', 'integrate.api.nvidia.com']));
    for (const h of derived) expect(LLM_HOSTS.has(h)).toBe(true);
    for (const h of ['api.x.ai', 'api.openai.com']) expect(isLlmHost(h)).toBe(true);
    expect(isLlmHost('example.com')).toBe(false);
  });

  it('real global fetch to an LLM host throws the clear blocked error', async () => {
    for (const url of [
      'https://api.groq.com/openai/v1/chat/completions',
      'https://api.x.ai/v1/chat/completions',
      'https://api.openai.com/v1/chat/completions',
      'https://integrate.api.nvidia.com/v1/chat/completions',
    ]) {
      const host = new URL(url).host;
      await expect(fetch(url, { method: 'POST' })).rejects.toThrow(
        `[vitest] blocked real LLM call to ${host}; mock fetch or opt in`,
      );
    }
  });

  it('node http/https requests to LLM hosts throw', () => {
    expect(() => https.request('https://api.groq.com/openai/v1')).toThrow(
      '[vitest] blocked real LLM call to api.groq.com',
    );
    expect(() => http.get({ hostname: 'api.openai.com', path: '/' })).toThrow(
      '[vitest] blocked real LLM call to api.openai.com',
    );
  });

  it('a stubbed fetch still works (mocks replace the guard)', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('{"ok":true}')));
    const r = await fetch('https://api.groq.com/openai/v1/chat/completions');
    expect(await r.json()).toEqual({ ok: true });
    vi.unstubAllGlobals();
    await expect(fetch('https://api.groq.com/x')).rejects.toThrow('blocked real LLM call');
  });
});
