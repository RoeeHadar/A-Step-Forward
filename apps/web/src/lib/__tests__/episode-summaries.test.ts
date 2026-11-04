import { describe, it, expect, vi } from 'vitest';
import {
  EPISODE_BLOCK_HEADER, EPISODE_MAX_CHARS, EPISODE_SUMMARIZER_MARKER, buildEpisodeBlock, episodeKey,
  episodeSummariesEnabled, estimateTokens, extractiveEpisodeSummary, selectEpisodes, shouldWriteEpisode,
  writeEpisodeSummary, type EpisodeNoteLike, type WriteEpisodeDeps,
} from '@/lib/episode-summaries';
import { decodeFactContent, encodeFactContent } from '@/lib/typed-facts';

const turns = (n: number) => Array.from({ length: n }, (_, i) => ({ role: (i % 2 ? 'assistant' : 'user') as 'user' | 'assistant', content: `turn ${i + 1} about derivatives` }));
const note = (id: string, sess: string, n: number, at: string, agent = 'tutor', text = `summary ${id}`): EpisodeNoteLike =>
  ({ id, agent, kind: 'episode', created_at: at, content: encodeFactContent(text, { key: episodeKey(sess)!, n, valid_to: null }) });

function deps(over: Partial<WriteEpisodeDeps> = {}) {
  const store: Array<{ kind: string; content: string; importance: number }> = [];
  const d: WriteEpisodeDeps = {
    fetchSessionTurns: async () => turns(4),
    complete: vi.fn(async () => 'Learner asked about d/dx cos x; answered sin x (sign error).'),
    fetchEpisodes: async () => [],
    append: vi.fn(async (n) => { store.push(n); return `id-${store.length}`; }),
    supersede: vi.fn(async () => undefined),
    warn: vi.fn(),
    ...over,
  };
  return { d, store };
}

describe('AS-57 episode summaries', () => {
  it('flag defaults off', () => {
    expect(episodeSummariesEnabled({})).toBe(false);
    for (const v of ['', '0', 'false', 'off', 'no']) expect(episodeSummariesEnabled({ EPISODE_SUMMARIES: v })).toBe(false);
    for (const v of ['1', 'true', 'ON']) expect(episodeSummariesEnabled({ EPISODE_SUMMARIES: v })).toBe(true);
  });

  it('write trigger: first exchange, then every K turns', () => {
    expect([1, 2, 3, 4, 5, 6, 7, 8].filter((n) => shouldWriteEpisode(n))).toEqual([2, 4, 8]);
  });

  it('writes an episode note with the session key and supersedes the previous one', async () => {
    const prev = note('old', 'sess-1', 2, '2026-01-01T00:00:00Z');
    const { d, store } = deps({ fetchEpisodes: async () => [prev, note('other', 'sess-2', 2, '2026-01-01T00:00:00Z')] });
    expect(await writeEpisodeSummary({ agent: 'tutor', sessionId: 'sess-1', locale: 'en' }, d)).toBe('written');
    expect(store).toHaveLength(1);
    expect(store[0]!.kind).toBe('episode');
    const dec = decodeFactContent(store[0]!.content);
    expect(dec.meta).toEqual({ key: 'session.sess-1', n: 4, valid_to: null });
    expect(d.supersede).toHaveBeenCalledTimes(1);
    expect(d.supersede).toHaveBeenCalledWith('old', 'id-1');
    const [sys] = (d.complete as ReturnType<typeof vi.fn>).mock.calls[0]! as [string, string];
    expect(sys.startsWith(EPISODE_SUMMARIZER_MARKER)).toBe(true);
  });

  it('skips without a session id or off-trigger', async () => {
    const { d } = deps({ fetchSessionTurns: async () => turns(3) });
    expect(await writeEpisodeSummary({ agent: 'tutor', sessionId: undefined, locale: 'en' }, d)).toBe('skipped');
    expect(await writeEpisodeSummary({ agent: 'tutor', sessionId: 's', locale: 'en' }, d)).toBe('skipped');
    expect(d.complete).not.toHaveBeenCalled();
  });

  it('summariser error / null → extractive fallback, never throws', async () => {
    const a = deps({ complete: async () => { throw new Error('boom'); } });
    expect(await writeEpisodeSummary({ agent: 'tutor', sessionId: 's', locale: 'en' }, a.d)).toBe('fallback');
    expect(decodeFactContent(a.store[0]!.content).text).toContain('learner: turn 1');
    const b = deps({ complete: async () => null });
    expect(await writeEpisodeSummary({ agent: 'tutor', sessionId: 's', locale: 'en' }, b.d)).toBe('fallback');
  });

  it('DB errors are swallowed (chat never breaks)', async () => {
    const { d } = deps({ append: async () => { throw new Error('db down'); } });
    await expect(writeEpisodeSummary({ agent: 'tutor', sessionId: 's', locale: 'en' }, d)).resolves.toBe('failed');
    const e = deps({ fetchSessionTurns: async () => { throw new Error('db down'); } });
    await expect(writeEpisodeSummary({ agent: 'tutor', sessionId: 's', locale: 'en' }, e.d)).resolves.toBe('failed');
  });

  it('caps summary length', async () => {
    const { d, store } = deps({ complete: async () => 'x'.repeat(2000) });
    await writeEpisodeSummary({ agent: 'tutor', sessionId: 's', locale: 'en' }, d);
    expect(decodeFactContent(store[0]!.content).text.length).toBeLessThanOrEqual(EPISODE_MAX_CHARS);
    expect(extractiveEpisodeSummary('tutor', turns(40)).length).toBeLessThanOrEqual(EPISODE_MAX_CHARS);
  });

  it('select: other sessions newest first, current session only past K, dedupe by key', () => {
    const notes = [
      note('a', 's1', 4, '2026-01-01T00:00:00Z'),
      note('b', 's2', 2, '2026-01-03T00:00:00Z'),
      note('c', 'cur', 4, '2026-01-04T00:00:00Z'),
      note('d', 's1', 2, '2025-12-31T00:00:00Z'),
    ];
    expect(selectEpisodes(notes, 'cur').map((n) => n.id)).toEqual(['b', 'a']);
    expect(selectEpisodes([...notes, note('e', 'cur', 6, '2026-01-05T00:00:00Z')], 'cur').map((n) => n.id)).toEqual(['e', 'b', 'a']);
    expect(selectEpisodes(notes, 'cur', 1).map((n) => n.id)).toEqual(['b']);
  });

  it('block: empty when nothing to inject, oldest first, envelope stripped', () => {
    expect(buildEpisodeBlock([])).toBe('');
    const b = buildEpisodeBlock(selectEpisodes([note('a', 's1', 4, '2026-01-01T00:00:00Z'), note('b', 's2', 4, '2026-01-02T00:00:00Z', 'coach')], undefined));
    expect(b.startsWith(EPISODE_BLOCK_HEADER)).toBe(true);
    expect(b.indexOf('summary a')).toBeLessThan(b.indexOf('summary b'));
    expect(b).not.toContain('⟦fact');
    expect(b).toContain('2026-01-02 coach:');
  });

  it('r1 P1-1: Date created_at (neon driver) is normalised, sorted and rendered', () => {
    const d = (id: string, sess: string, iso: string) => ({ ...note(id, sess, 4, iso), created_at: new Date(iso) });
    const sel = selectEpisodes([d('a', 's1', '2026-01-01T10:00:00Z'), d('b', 's2', '2026-01-03T10:00:00Z'), note('c', 's3', 4, '2026-01-02T10:00:00Z')], 'cur');
    expect(sel.map((n) => n.id)).toEqual(['b', 'c', 'a']);
    const b = buildEpisodeBlock(sel);
    expect(b).toContain('- 2026-01-01 tutor: summary a');
    expect(b).toContain('- 2026-01-03 tutor: summary b');
  });

  it('token estimate: Hebrew ≈2 chars/token, Latin ≈4', () => {
    expect(estimateTokens('')).toBe(0);
    expect(estimateTokens('abcdefgh')).toBe(2);
    expect(estimateTokens('שלוםשלום')).toBe(4);
    const raw = turns(8).map((t) => `${t.role}: ${t.content}`).join('\n');
    expect(estimateTokens('summary: derivatives, sign error')).toBeLessThan(estimateTokens(raw) * 0.7);
  });
});
