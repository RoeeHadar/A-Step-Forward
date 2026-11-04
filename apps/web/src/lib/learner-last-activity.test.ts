import { describe, expect, it, vi, beforeEach, afterAll } from 'vitest';

// AS-47: read-only learner-wide last-activity query — exercised against a mocked
// neon tagged-template (no DB, no network).
const calls: Array<{ text: string; values: unknown[] }> = [];
let nextRows: unknown[] | Error = [];
const mockSql = vi.fn((strings: TemplateStringsArray, ...values: unknown[]) => {
  calls.push({ text: strings.join('?'), values });
  return nextRows instanceof Error ? Promise.reject(nextRows) : Promise.resolve(nextRows);
});
vi.mock('server-only', () => ({}));
// AS-65: restore DATABASE_URL (set in the mock factory below) so single-fork runs don't leak it.
const AS65_DB_URL = vi.hoisted(() => process.env.DATABASE_URL);
afterAll(() => {
  if (AS65_DB_URL === undefined) delete process.env.DATABASE_URL;
  else process.env.DATABASE_URL = AS65_DB_URL;
});
vi.mock('@neondatabase/serverless', () => {
  process.env['DATABASE_URL'] = 'postgresql://placeholder-as47';
  return { neon: () => mockSql, neonConfig: {} };
});

const { fetchLearnerLastActivityAt } = await import('./neon-db');

describe('AS-47 fetchLearnerLastActivityAt', () => {
  beforeEach(() => { calls.length = 0; nextRows = []; vi.spyOn(console, 'warn').mockImplementation(() => {}); });

  it('is a single read-only SELECT over chat_turns / skill_practice / test_attempts scoped to one learner, before cutoff', async () => {
    nextRows = [{ last_at: '2026-01-05T09:00:00.000Z' }];
    const before = new Date('2026-01-17T09:00:00.000Z');
    const r = await fetchLearnerLastActivityAt('learner-A', before);
    expect(r).toBe('2026-01-05T09:00:00.000Z');
    expect(calls).toHaveLength(1);
    const { text, values } = calls[0]!;
    expect(text.trim().toUpperCase().startsWith('SELECT')).toBe(true);
    expect(text).not.toMatch(/\b(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE)\b/i);
    expect(text).toMatch(/FROM chat_turns[\s\S]*learner_id = \?[\s\S]*created_at < \?/);
    expect(text).toMatch(/FROM skill_practice[\s\S]*last_practiced < \?/);
    expect(text).toMatch(/FROM test_attempts[\s\S]*created_at < \?/);
    expect(text).not.toMatch(/\bagent\s*=/); // learner-wide across agents
    expect(text).not.toMatch(/content/); // timestamp only, no turn/note text
    expect(values).toEqual(['learner-A', before.toISOString(), 'learner-A', before.toISOString(), 'learner-A', before.toISOString()]);
  });

  it('normalises Date rows; null / error / blank learner → null', async () => {
    nextRows = [{ last_at: new Date('2026-01-01T00:00:00Z') }];
    expect(await fetchLearnerLastActivityAt('x', new Date())).toBe('2026-01-01T00:00:00.000Z');
    nextRows = [{ last_at: null }];
    expect(await fetchLearnerLastActivityAt('x', new Date())).toBeNull();
    nextRows = new Error('relation "test_attempts" does not exist');
    expect(await fetchLearnerLastActivityAt('x', new Date())).toBeNull();
    calls.length = 0;
    expect(await fetchLearnerLastActivityAt('  ', new Date())).toBeNull();
    expect(calls).toHaveLength(0);
  });

  it('AS-48: a turn 30 s before the request counts; the current turn (recorded after request start) does not', async () => {
    const requestStartedAt = new Date('2026-01-17T09:00:00.000Z');
    const rows = [
      { table: 'chat_turns', learner_id: 'learner-A', at: '2026-01-17T08:59:30.000Z' }, // 30 s before → prior
      { table: 'chat_turns', learner_id: 'learner-A', at: '2026-01-17T09:00:00.000Z' }, // == start → excluded (strict <)
      { table: 'chat_turns', learner_id: 'learner-A', at: '2026-01-17T09:00:00.120Z' }, // current turn, saved after start
      { table: 'chat_turns', learner_id: 'learner-B', at: '2026-01-17T08:59:59.000Z' }, // other learner
    ];
    // Evaluate the query's WHERE semantics (learner_id = $1 AND ts < $2) over fixture rows.
    mockSql.mockImplementationOnce((strings: TemplateStringsArray, ...values: unknown[]) => {
      calls.push({ text: strings.join('?'), values });
      expect(strings.join('?')).toMatch(/created_at < \?/);
      const [learner, cutoff] = values as [string, string];
      const hits = rows.filter((r) => r.learner_id === learner && r.at < cutoff).map((r) => r.at).sort();
      return Promise.resolve([{ last_at: hits.at(-1) ?? null }]);
    });
    const r = await fetchLearnerLastActivityAt('learner-A', requestStartedAt);
    expect(calls[0]!.values[1]).toBe(requestStartedAt.toISOString()); // exact request start, no 60 s window
    expect(r).toBe('2026-01-17T08:59:30.000Z');
  });
});
