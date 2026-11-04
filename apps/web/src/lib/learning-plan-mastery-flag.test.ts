/** AS-51: MASTERY_MODEL off (unset / 'ratio') is byte-identical to the pre-AS-51 read. */
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));
const ROWS = [
  { skill_atom: 'Order of operations (PEMDAS/BODMAS)', attempts: 6, successes: 3, staleness_days: 2 },
  { skill_atom: 'Working with negative numbers', attempts: 3, successes: 0, staleness_days: null },
  { skill_atom: 'Identifying and combining like terms', attempts: 7, successes: 6, staleness_days: 0.5 },
  { skill_atom: 'Solving single linear equation in one unknown', attempts: 0, successes: 0, staleness_days: 9 },
];
vi.mock('@neondatabase/serverless', () => ({
  neon: () => async (strings: TemplateStringsArray) => {
    const q = strings.join('?');
    if (q.includes('FROM skill_practice')) return ROWS;
    if (q.includes('FROM lesson_skill_atoms')) return [
      { concept_id: 'arithmetic', skill_atom: ROWS[0]!.skill_atom }, { concept_id: 'arithmetic', skill_atom: ROWS[1]!.skill_atom },
      { concept_id: 'algebra_basics', skill_atom: ROWS[2]!.skill_atom }, { concept_id: 'equations_linear', skill_atom: ROWS[3]!.skill_atom },
    ];
    return [];
  },
}));

type LP = typeof import('./learning-plan');
let lp: LP;
beforeAll(async () => {
  process.env.DATABASE_URL = 'postgres://placeholder.invalid/db'; // placeholder only; neon is mocked
  vi.useFakeTimers({ toFake: ['Date'] });
  vi.setSystemTime(Date.UTC(2026, 0, 5, 9));
  lp = await import('./learning-plan');
});
afterAll(() => { vi.useRealTimers(); delete process.env.DATABASE_URL; delete process.env.MASTERY_MODEL; });

/** Pre-AS-51 formula (learning-plan.ts:112 @ 99c61fb9), verbatim. */
const legacy = (r: (typeof ROWS)[number]) => (r.attempts > 0 ? r.successes / r.attempts : 0);

describe('AS-51 flag off = unchanged', () => {
  it('fetchLearnerMastery: unset and ratio equal the legacy formula exactly', async () => {
    delete process.env.MASTERY_MODEL;
    const a = await lp.fetchLearnerMastery('L');
    process.env.MASTERY_MODEL = 'ratio';
    const b = await lp.fetchLearnerMastery('L');
    for (const r of ROWS) expect(a.get(r.skill_atom)!.mastery).toBe(legacy(r));
    expect(JSON.stringify([...b])).toBe(JSON.stringify([...a]));
  });
  it('buildLearningPlan output is byte-identical with the flag unset vs ratio vs bkt-without-attempts', async () => {
    delete process.env.MASTERY_MODEL;
    const a = JSON.stringify(await lp.buildLearningPlan({ learnerId: 'L', goalConceptId: 'equations_linear' }));
    process.env.MASTERY_MODEL = 'ratio';
    const b = JSON.stringify(await lp.buildLearningPlan({ learnerId: 'L', goalConceptId: 'equations_linear' }));
    process.env.MASTERY_MODEL = 'bkt'; // no ordered-attempt source -> ratio fallback
    const c = JSON.stringify(await lp.buildLearningPlan({ learnerId: 'L', goalConceptId: 'equations_linear' }));
    expect(a).toContain('Working with negative numbers');
    expect(b).toBe(a);
    expect(c).toBe(a);
  });
  it('bkt with ordered attempts changes mastery (replay)', async () => {
    const m = await lp.fetchLearnerMastery('L', { model: 'bkt', orderedAttempts: new Map([['Order of operations (PEMDAS/BODMAS)', [false, false, false, true, true, true]]]) });
    expect(m.get('Order of operations (PEMDAS/BODMAS)')!.mastery).toBeGreaterThanOrEqual(0.8);
    expect(m.get('Working with negative numbers')!.mastery).toBe(0);
  });
});
