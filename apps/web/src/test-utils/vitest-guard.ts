/**
 * AS-67 global vitest setup (wired via `test.setupFiles` in vitest.config.ts).
 *
 * 1. Per-file env isolation: setup files run once per test FILE, before the file is imported,
 *    so the snapshot below captures env before any top-level test code runs. afterAll restores
 *    process.env IN PLACE (deletes added keys, resets changed ones; never reassigns process.env).
 * 2. Real-LLM block: the real global fetch and node:http/https request/get throw
 *    `[vitest] blocked real LLM call to <host>; mock fetch or opt in` for LLM hosts. Tests that
 *    replace fetch (vi.fn / vi.stubGlobal / spyOn) are unaffected. Hosts are derived from
 *    src/lib/llm-provider.ts URL literals plus a static list of known providers.
 *    Opt in (real calls, e.g. *.llm.integration suites): `ALLOW_REAL_LLM=1 npx vitest run ...`
 */
import fs from 'node:fs';
import http from 'node:http';
import https from 'node:https';
import path from 'node:path';
import { afterAll } from 'vitest';

export type EnvSnapshot = Record<string, string | undefined>;

export function snapshotEnv(env: NodeJS.ProcessEnv = process.env): EnvSnapshot {
  return { ...env };
}

/** Restore `env` in place to `snap`. Returns the keys that were changed/removed. */
export function restoreEnv(snap: EnvSnapshot, env: NodeJS.ProcessEnv = process.env): string[] {
  const touched: string[] = [];
  for (const key of Object.keys(env)) {
    if (!(key in snap)) {
      delete env[key];
      touched.push(key);
    }
  }
  for (const [key, value] of Object.entries(snap)) {
    if (value === undefined) continue;
    if (env[key] !== value) {
      env[key] = value;
      touched.push(key);
    }
  }
  return touched;
}

export const STATIC_LLM_HOSTS = [
  'api.groq.com',
  'api.x.ai',
  'api.openai.com',
  'integrate.api.nvidia.com',
  'openrouter.ai',
  'api.together.xyz',
  'api.together.ai',
  'api.fireworks.ai',
  'api.anthropic.com',
  'generativelanguage.googleapis.com',
];

/** URL hosts found in llm-provider.ts source, so new defaults stay covered automatically. */
export function hostsFromProviderSource(source: string): string[] {
  const out = new Set<string>();
  for (const m of source.matchAll(/https?:\/\/([a-z0-9.-]+\.[a-z]{2,})/gi)) out.add(m[1]!.toLowerCase());
  return [...out];
}

function loadLlmHosts(): Set<string> {
  const hosts = new Set(STATIC_LLM_HOSTS);
  try {
    const src = fs.readFileSync(path.resolve(__dirname, '../lib/llm-provider.ts'), 'utf8');
    for (const h of hostsFromProviderSource(src)) hosts.add(h);
  } catch {
    /* static list still applies */
  }
  return hosts;
}

export const LLM_HOSTS = loadLlmHosts();

export function isLlmHost(host: string | null | undefined): boolean {
  if (!host) return false;
  const h = host.toLowerCase().replace(/:\d+$/, '');
  for (const known of LLM_HOSTS) if (h === known || h.endsWith(`.${known}`)) return true;
  return false;
}

export function blockedError(host: string): Error {
  return new Error(`[vitest] blocked real LLM call to ${host}; mock fetch or opt in (ALLOW_REAL_LLM=1)`);
}

function hostOfFetchInput(input: unknown): string | null {
  try {
    if (typeof input === 'string') return new URL(input).host;
    if (input instanceof URL) return input.host;
    if (input && typeof (input as Request).url === 'string') return new URL((input as Request).url).host;
  } catch {
    /* relative/invalid URL: not an LLM host */
  }
  return null;
}

function hostOfHttpArgs(args: unknown[]): string | null {
  const a = args[0];
  if (typeof a === 'string' || a instanceof URL) return hostOfFetchInput(a);
  if (a && typeof a === 'object') {
    const o = a as { hostname?: string; host?: string };
    return o.hostname ?? o.host ?? null;
  }
  return null;
}

export const realLlmAllowed = () => process.env.ALLOW_REAL_LLM === '1';

const GUARD = Symbol.for('asf.vitest.llmGuard');

function installGuards(): void {
  const g = globalThis as typeof globalThis & { [GUARD]?: boolean };
  if (g[GUARD]) return;
  g[GUARD] = true;

  if (typeof globalThis.fetch === 'function') {
    const realFetch = globalThis.fetch;
    const guarded = function guardedFetch(input: Parameters<typeof fetch>[0], init?: RequestInit) {
      const host = hostOfFetchInput(input);
      if (!realLlmAllowed() && isLlmHost(host)) return Promise.reject(blockedError(host!));
      return realFetch(input, init);
    } as typeof fetch;
    globalThis.fetch = guarded;
  }

  for (const mod of [http, https] as const) {
    for (const fn of ['request', 'get'] as const) {
      const orig = mod[fn] as (...a: unknown[]) => http.ClientRequest;
      (mod as unknown as Record<string, unknown>)[fn] = function guardedHttp(...args: unknown[]) {
        const host = hostOfHttpArgs(args);
        if (!realLlmAllowed() && isLlmHost(host)) throw blockedError(host!);
        return orig.apply(mod, args);
      };
    }
  }
}

installGuards();

const fileEnvSnapshot = snapshotEnv();
afterAll(() => {
  restoreEnv(fileEnvSnapshot);
});
