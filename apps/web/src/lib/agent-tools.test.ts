import { beforeEach, describe, expect, it, vi } from 'vitest';

const { retrieveChunks } = vi.hoisted(() => ({
  retrieveChunks: vi.fn(),
}));

vi.mock('@/lib/rag-retrieve', () => ({
  retrieveChunks: (...args: unknown[]) => retrieveChunks(...args),
  detectLang: () => 'he',
}));

import { corpusMissObservation, getReadOnlyTools } from './agent-tools';

const retrieve = getReadOnlyTools().find((t) => t.spec.function.name === 'retrieve')!;

describe('retrieve tool (ADR-0015 corpus miss)', () => {
  beforeEach(() => retrieveChunks.mockReset());

  it('uses the general-knowledge observation when the corpus is empty', async () => {
    retrieveChunks.mockResolvedValueOnce([]);
    const res = await retrieve.handler({ query: 'נגזרת' }, { userId: 'u', agent: 'tutor', locale: 'he' });
    expect(res.observation).toBe(corpusMissObservation());
    expect(res.observation).toMatch(/general knowledge/i);
  });

  it('uses the same observation when retrieve throws (does not say temporarily unavailable)', async () => {
    retrieveChunks.mockRejectedValueOnce(new Error('embed down'));
    const res = await retrieve.handler({ query: 'נגזרת' }, { userId: 'u', agent: 'tutor', locale: 'he' });
    expect(res.observation).toBe(corpusMissObservation());
    expect(res.observation).not.toMatch(/temporarily unavailable/i);
  });
});
