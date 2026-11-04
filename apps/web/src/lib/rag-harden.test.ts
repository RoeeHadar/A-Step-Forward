/**
 * AS-72: RAG hardening — once-only empty/missing-corpus warning, relevance
 * floor, and the ingest target guard. DB, embedder and logger are mocked; no
 * network or DB access.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { spawnSync } from 'node:child_process';
import path from 'node:path';

const state: { mode: 'empty' | 'missing' | 'rows'; rows: Array<Record<string, unknown>> } = {
  mode: 'empty',
  rows: [],
};
const sqlMock = vi.fn(async (strings: TemplateStringsArray) => {
  const q = strings.join('?');
  if (q.includes('SELECT 1 AS ok FROM kg_chunks')) {
    if (state.mode === 'missing') {
      throw Object.assign(new Error('relation "kg_chunks" does not exist'), { code: '42P01' });
    }
    return state.mode === 'empty' ? [] : [{ ok: 1 }];
  }
  return state.rows;
});
const warn = vi.fn();

vi.mock('server-only', () => ({}));
vi.mock('@neondatabase/serverless', () => ({ neon: () => sqlMock }));
vi.mock('@/lib/logger', () => ({
  logger: { warn: (...a: unknown[]) => warn(...a), error: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));
vi.mock('@/lib/rag-embed', () => ({ embedQuery: vi.fn(async () => [0.1, 0.2]) }));

async function load() {
  vi.resetModules();
  process.env.DATABASE_URL = 'postgres://placeholder@localhost/placeholder';
  return import('./rag-retrieve');
}

const corpusWarns = () =>
  warn.mock.calls.filter((c) => String(c[0]).includes('corpus not available'));

beforeEach(() => {
  warn.mockClear();
  sqlMock.mockClear();
  vi.useFakeTimers();
});
afterEach(() => {
  vi.useRealTimers();
  delete process.env.RAG_MIN_SCORE;
});

describe('kg_chunks not available → one warning per instance', () => {
  for (const mode of ['empty', 'missing'] as const) {
    it(`warns exactly once across repeated calls (${mode})`, async () => {
      state.mode = mode;
      const m = await load();
      for (let i = 0; i < 5; i++) {
        expect(await m.retrieveChunks({ query: 'what is a limit?' })).toEqual([]);
        vi.advanceTimersByTime(6 * 60 * 1000); // past the 5-min re-probe TTL
      }
      expect(sqlMock.mock.calls.length).toBeGreaterThanOrEqual(5); // re-probed
      expect(corpusWarns()).toHaveLength(1);
      expect(corpusWarns()[0]?.[1]).toMatchObject({ reason: mode });
      if (mode === 'missing') expect(corpusWarns()[0]?.[1]).toMatchObject({ code: '42P01' });
    });
  }

  it('does not warn when the corpus has rows', async () => {
    state.mode = 'rows';
    state.rows = [];
    const m = await load();
    await m.retrieveChunks({ query: 'what is a limit?' });
    expect(corpusWarns()).toHaveLength(0);
  });
});

describe('relevance floor', () => {
  const row = (id: string, score: number) => ({
    id, text: id, heading: null, source_type: 'lesson', source_doc_id: id,
    concept_id: null, title: null, score,
  });

  it('is 2/(60+40) = 0.02 (two channels must agree)', async () => {
    const m = await load();
    expect(m.RAG_MIN_FUSED_SCORE).toBeCloseTo(0.02, 10);
    // a single channel can never reach it, two channels at the window edge can
    expect(1 / 61).toBeLessThan(m.RAG_MIN_FUSED_SCORE);
    expect(2 / 100).toBeGreaterThanOrEqual(m.RAG_MIN_FUSED_SCORE);
  });

  it('drops below-floor chunks and keeps above-floor ones in retrieveChunks', async () => {
    state.mode = 'rows';
    state.rows = [row('strong', 0.032), row('edge', 0.02), row('weak', 0.0164), row('junk', 0.01)];
    const m = await load();
    const out = await m.retrieveChunks({ query: 'what is a limit?' });
    expect(out.map((c) => c.id)).toEqual(['strong', 'edge']);
  });

  it('honours RAG_MIN_SCORE override (0 disables)', async () => {
    const m = await load();
    const chunks = [0.03, 0.005].map((score, i) => ({
      id: String(i), text: '', heading: null, sourceType: 'lesson', sourceDocId: String(i),
      conceptId: null, title: null, score, channel: 'hybrid' as const,
    }));
    process.env.RAG_MIN_SCORE = '0';
    expect(m.applyRelevanceFloor(chunks)).toHaveLength(2);
    process.env.RAG_MIN_SCORE = 'nonsense';
    expect(m.applyRelevanceFloor(chunks)).toHaveLength(1);
  });
});

describe('ingest target guard', () => {
  // @ts-expect-error plain .mjs module without types
  const guardP = import('../../../../scripts/lib/rag-ingest-guard.mjs');

  it('defaults to dev', async () => {
    const { checkIngestTarget } = await guardP;
    expect(checkIngestTarget({})).toEqual({ ok: true, target: 'dev' });
    expect(checkIngestTarget({ recreateSchema: true, fresh: true })).toMatchObject({ ok: true, target: 'dev' });
  });

  it('refuses production + recreate_schema / fresh without confirm', async () => {
    const { checkIngestTarget } = await guardP;
    expect(checkIngestTarget({ target: 'production', recreateSchema: true })).toMatchObject({ ok: false });
    expect(checkIngestTarget({ target: 'production', fresh: true })).toMatchObject({ ok: false });
    expect(checkIngestTarget({ target: 'prod' })).toMatchObject({ ok: false });
  });

  it('proceeds for production with the confirm flag (or non-destructive)', async () => {
    const { checkIngestTarget, parseIngestArgs } = await guardP;
    expect(
      checkIngestTarget(parseIngestArgs(['--target', 'production', '--recreate-schema', '--confirm-production'])),
    ).toEqual({ ok: true, target: 'production' });
    expect(checkIngestTarget({ target: 'production' })).toEqual({ ok: true, target: 'production' });
  });

  it('script --guard-only exits before any env/DB access', () => {
    const root = path.resolve(__dirname, '../../../..');
    const run = (args: string[]) =>
      spawnSync(process.execPath, ['scripts/rag-ingest.mjs', '--guard-only', ...args], {
        cwd: root,
        env: { PATH: process.env.PATH ?? '' } as unknown as NodeJS.ProcessEnv, // no DATABASE_URL / keys
        encoding: 'utf8',
      });
    const refused = run(['--target', 'production', '--recreate-schema']);
    expect(refused.status).toBe(1);
    expect(refused.stderr).toContain('REFUSING');
    const ok = run(['--target', 'production', '--recreate-schema', '--confirm-production']);
    expect(ok.status).toBe(0);
    expect(ok.stdout).toContain('ingest target: production');
  });
});
