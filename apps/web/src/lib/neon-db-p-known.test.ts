/**
 * AS-53 (C5b): skill_practice.p_known at the two practice write sites in neon-db.ts
 * (applyPracticeMasteryUpdate via recordCustomQuizPractice / recordLessonAnswer, and
 * markAtomPracticed). MASTERY_MODEL unset/'ratio' must issue exactly the pre-AS-53 statements;
 * 'bkt' adds the column guard, reads the prior and writes bktUpdate(prior ?? p_init, correct).
 * Fake SQL only: no DB, no network.
 */
import { afterAll, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { BKT_GLOBAL_PARAMS, bktUpdate } from './bkt';

vi.mock('server-only', () => ({}));
vi.mock('./adaptive-plan-refresh', () => ({ scheduleAdaptivePlanRefresh: () => {} }));
vi.mock('./learner-xp', () => ({ maybeAwardMasteryXp: async () => {}, maybeAwardStreakXp: async () => {} }));

type Call = { q: string; v: unknown[] };
const calls: Call[] = [];
const priors = new Map<string, string | number | null>();
vi.mock('@neondatabase/serverless', () => ({
  neonConfig: {},
  neon: () => async (strings: TemplateStringsArray, ...values: unknown[]) => {
    const q = strings.join('$');
    calls.push({ q, v: values });
    if (q.includes('SELECT p_known FROM skill_practice')) {
      const k = `${values[0]}|${values[1]}`;
      return priors.has(k) ? [{ p_known: priors.get(k) }] : [];
    }
    return [];
  },
}));

type Db = typeof import('./neon-db');
let db: Db;
beforeAll(async () => {
  process.env.DATABASE_URL = 'postgres://placeholder.invalid/db'; // placeholder only; neon is mocked
  db = await import('./neon-db');
});
beforeEach(() => {
  calls.length = 0;
  priors.clear();
  delete process.env.MASTERY_MODEL;
});
afterAll(() => {
  delete process.env.DATABASE_URL;
  delete process.env.MASTERY_MODEL;
});

const norm = (q: string) => q.replace(/\s+/g, ' ').trim();
const spCalls = () => calls.filter((c) => c.q.includes('skill_practice'));

/** Pre-AS-53 statements (neon-db.ts @ tree 5c696a93), whitespace-normalised, values verbatim. */
const LEGACY_SITE1 =
  'INSERT INTO skill_practice (learner_id, skill_atom, attempts, successes, last_practiced) VALUES ($, $, 1, $, NOW()) ON CONFLICT (learner_id, skill_atom) DO UPDATE SET attempts = skill_practice.attempts + 1, successes = skill_practice.successes + $, last_practiced = NOW()';
const LEGACY_SITE2 =
  "INSERT INTO skill_practice ( learner_id, skill_atom, attempts, successes, last_practiced, last_score, next_review_date ) VALUES ( $, $, 1, $, NOW(), $, NOW() + ($ || ' days')::interval ) ON CONFLICT (learner_id, skill_atom) DO UPDATE SET attempts = skill_practice.attempts + 1, successes = skill_practice.successes + $, last_practiced = NOW(), last_score = $, next_review_date = NOW() + ($ || ' days')::interval";

describe('AS-53 flag off = pre-AS-53 statements', () => {
  for (const flag of [undefined, 'ratio', 'BKT', ''] as const) {
    it(`site 1 applyPracticeMasteryUpdate, MASTERY_MODEL=${String(flag)}`, async () => {
      if (flag !== undefined) process.env.MASTERY_MODEL = flag;
      await db.recordCustomQuizPractice({ learnerId: 'L1', conceptId: 'c1', correct: true, skillAtoms: ['a1', '', 'a2'] });
      await db.recordCustomQuizPractice({ learnerId: 'L1', conceptId: 'c1', correct: false, skillAtoms: ['a1'] });
      const sp = spCalls();
      expect(sp.map((c) => norm(c.q))).toEqual([LEGACY_SITE1, LEGACY_SITE1, LEGACY_SITE1]);
      expect(sp.map((c) => c.v)).toEqual([['L1', 'a1', 1, 1], ['L1', 'a2', 1, 1], ['L1', 'a1', 0, 0]]);
      expect(calls.some((c) => c.q.includes('p_known'))).toBe(false);
    });
    it(`site 2 markAtomPracticed, MASTERY_MODEL=${String(flag)}`, async () => {
      if (flag !== undefined) process.env.MASTERY_MODEL = flag;
      await db.markAtomPracticed('U1', 'a1', 0.85);
      await db.markAtomPracticed('U1', 'a1', 0.4);
      const ins = spCalls().filter((c) => c.q.includes('INSERT'));
      expect(ins.map((c) => norm(c.q))).toEqual([LEGACY_SITE2, LEGACY_SITE2]);
      expect(ins.map((c) => c.v)).toEqual([['U1', 'a1', 1, 0.85, 7, 1, 0.85, 7], ['U1', 'a1', 0, 0.4, 1, 0, 0.4, 1]]);
      expect(calls.some((c) => c.q.includes('p_known'))).toBe(false);
    });
  }
});

describe('AS-53 flag on (MASTERY_MODEL=bkt) writes p_known', () => {
  it('site 1: new row starts from p_init; stored prior is updated; wrong answers lower it', async () => {
    process.env.MASTERY_MODEL = 'bkt';
    priors.set('L2|a2', '0.5'); // NUMERIC comes back as a string from neon
    await db.recordCustomQuizPractice({ learnerId: 'L2', conceptId: 'c1', correct: true, skillAtoms: ['a1', 'a2'] });
    const ups = spCalls().filter((c) => c.q.includes('INSERT'));
    expect(ups).toHaveLength(2);
    for (const c of ups) expect(norm(c.q)).toContain('last_practiced = NOW(), p_known = $');
    const pk0 = bktUpdate(BKT_GLOBAL_PARAMS.p_init, true);
    expect(ups[0]!.v).toEqual(['L2', 'a1', 1, pk0, 1, pk0]);
    expect(ups[1]!.v.at(-1)).toBeCloseTo(bktUpdate(0.5, true), 12);
    expect(bktUpdate(0.5, true)).toBeGreaterThan(0.5);

    calls.length = 0;
    priors.set('L2|a2', null); // NULL p_known (pre-migration row) -> p_init
    await db.recordCustomQuizPractice({ learnerId: 'L2', conceptId: 'c1', correct: false, skillAtoms: ['a2'] });
    const w = spCalls().filter((c) => c.q.includes('INSERT'));
    expect(w[0]!.v).toEqual(['L2', 'a2', 0, bktUpdate(0.2, false), 0, bktUpdate(0.2, false)]);
    expect(bktUpdate(0.2, false)).toBeLessThan(0.2);
  });

  it('site 1: column guard runs once per process, before the first read; skipped atoms are not read', async () => {
    vi.resetModules(); // fresh module = fresh column-guard memo
    const fresh = await import('./neon-db');
    process.env.MASTERY_MODEL = 'bkt';
    await fresh.recordCustomQuizPractice({ learnerId: 'L3', conceptId: 'c1', correct: true, skillAtoms: ['', 'a1'] });
    await fresh.markAtomPracticed('L3', 'a1', 0.9);
    const qs = calls.map((c) => norm(c.q));
    const alters = qs.filter((q) => q === 'ALTER TABLE skill_practice ADD COLUMN IF NOT EXISTS p_known NUMERIC');
    expect(alters).toHaveLength(1);
    expect(qs.indexOf(alters[0]!)).toBeLessThan(qs.findIndex((q) => q.startsWith('SELECT p_known')));
    expect(calls.filter((c) => c.q.includes('SELECT p_known')).map((c) => c.v)).toEqual([['L3', 'a1'], ['L3', 'a1']]);
  });

  it('site 2: observation is the >= 0.6 cut, same as successes; FSRS fields unchanged', async () => {
    process.env.MASTERY_MODEL = 'bkt';
    priors.set('U2|a1', 0.3);
    await db.markAtomPracticed('U2', 'a1', 0.6);
    await db.markAtomPracticed('U2', 'a9', 0.59);
    const ins = spCalls().filter((c) => c.q.includes('INSERT'));
    expect(ins).toHaveLength(2);
    for (const c of ins) expect(norm(c.q)).toContain("next_review_date = NOW() + ($ || ' days')::interval, p_known = $");
    expect(ins[0]!.v).toEqual(['U2', 'a1', 1, 0.6, 3, bktUpdate(0.3, true), 1, 0.6, 3, bktUpdate(0.3, true)]);
    expect(ins[1]!.v).toEqual(['U2', 'a9', 0, 0.59, 1, bktUpdate(0.2, false), 0, 0.59, 1, bktUpdate(0.2, false)]);
  });

  it('site 2: score is clamped before the observation (1.7 -> 1 correct, -1 -> 0 wrong)', async () => {
    process.env.MASTERY_MODEL = 'bkt';
    await db.markAtomPracticed('U3', 'a1', 1.7);
    await db.markAtomPracticed('U3', 'a2', -1);
    const ins = spCalls().filter((c) => c.q.includes('INSERT'));
    expect(ins[0]!.v.at(-1)).toBe(bktUpdate(0.2, true));
    expect(ins[1]!.v.at(-1)).toBe(bktUpdate(0.2, false));
  });
});
