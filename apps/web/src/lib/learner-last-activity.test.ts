import { describe, expect, it, vi, beforeEach } from 'vitest';

// AS-47: read-only learner-wide last-activity query — exercised against a mocked
// neon tagged-template (no DB, no network).
const calls: Array<{ text: string; values: unknown[] }> = [];
let nextRows: unknown[] | Error = [];
const mockSql = vi.fn((strings: TemplateStringsArray, ...values: unknown[]) => {
  calls.push({ text: strings.join('?'), values });
  return nextRows instanceof Error ? Promise.reject(nextRows) : Promise.resolve(nextRows);
});
vi.mock('server-only', () => ({}));
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
});
