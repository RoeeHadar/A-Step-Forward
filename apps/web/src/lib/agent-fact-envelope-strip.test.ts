/** AS-55 (C3c): the typed-fact envelope never reaches dedup, the LLM note list, or the notes API. */
import { describe, it, expect, vi } from 'vitest';

vi.mock('server-only', () => ({}));
vi.mock('@neondatabase/serverless', () => ({ neon: () => null, neonConfig: {} }));
const notes = vi.hoisted(() => ({ rows: [] as unknown[] }));
vi.mock('@/lib/neon-db', () => ({
  dbConfigured: true,
  ensureMemoryClaimColumns: vi.fn(async () => undefined),
  supersedeAgentNote: vi.fn(async () => undefined),
  appendAgentNote: vi.fn(async () => 'x'),
  fetchAgentNotes: vi.fn(async () => notes.rows),
}));
vi.mock('@/lib/web-agents', () => ({ WEB_LIVE_AGENTS: ['tutor', 'mentor'] as readonly string[] }));
vi.mock('@clerk/nextjs/server', () => ({ auth: async () => ({ userId: 'u-test' }) }));

import { encodeFactContent } from '@/lib/typed-facts';
import { tokenSet, jaccard, DUP_JACCARD } from '@/lib/agent-memory-dream';
import { formatMemoryExpandToolResult } from '@/lib/agent-hybrid-tools';
import type { LearnerAgentNote } from '@/lib/neon-db';

const ENVELOPE_TOKENS = /⟦fact|valid_to|"key"|"n":/;
const examFact = encodeFactContent('exam in 2 weeks', { key: 'goal:exam_date', n: 1, valid_to: null });
const langFact = encodeFactContent('prefers Hebrew', { key: 'preference:language', n: 1, valid_to: null });
const note = (id: string, content: string): LearnerAgentNote => ({
  id, learner_id: 'u-test', agent: 'mentor', kind: 'goal', content, importance: 3,
  related_concept_id: null, source_turn_id: null, created_at: new Date('2026-01-01T00:00:00Z'), last_referenced_at: null,
});

describe('dream dedup ignores the fact envelope', () => {
  it('two different short typed facts are not duplicates', () => {
    expect(examFact).toMatch(ENVELOPE_TOKENS);
    const a = tokenSet(examFact);
    const b = tokenSet(langFact);
    expect([...a, ...b].some((t) => /fact|valid_to|key|null/.test(t))).toBe(false);
    expect(jaccard(a, b)).toBeLessThan(DUP_JACCARD);
  });
  it('the same fact text is still a duplicate', () => {
    const again = encodeFactContent('exam in 2 weeks', { key: 'goal:exam_date', n: 2, valid_to: null });
    expect(jaccard(tokenSet(examFact), tokenSet(again))).toBeGreaterThanOrEqual(DUP_JACCARD);
  });
});

describe('envelope never reaches the LLM note list', () => {
  it('memory.expand tool result shows display text only', () => {
    const out = formatMemoryExpandToolResult([note('1', examFact), note('2', langFact)]);
    expect(out).toContain('exam in 2 weeks');
    expect(out).toContain('prefers Hebrew');
    expect(out).not.toMatch(ENVELOPE_TOKENS);
  });
});

describe('envelope never reaches the notes API response', () => {
  it('GET /api/agent-memory/notes strips the envelope', async () => {
    notes.rows = [note('1', examFact), note('2', 'plain observation')];
    const { GET } = await import('@/app/api/agent-memory/notes/route');
    const res = await GET(new Request('http://localhost/api/agent-memory/notes?agent=mentor'));
    const body = (await res.json()) as { notes: LearnerAgentNote[] };
    expect(body.notes.map((n) => n.content)).toEqual(['exam in 2 weeks', 'plain observation']);
    expect(JSON.stringify(body)).not.toMatch(ENVELOPE_TOKENS);
  });
});
