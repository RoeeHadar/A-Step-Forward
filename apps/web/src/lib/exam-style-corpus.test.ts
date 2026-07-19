import { describe, expect, it } from 'vitest';
import {
  examStyleCorpusStats,
  formatExamStyleStem,
  pickExamStyleItems,
} from './exam-style-corpus';

describe('exam-style-corpus', () => {
  it('has a non-trivial generated corpus', () => {
    const stats = examStyleCorpusStats();
    expect(stats.count).toBeGreaterThanOrEqual(200);
    expect(stats.by_goal.bagrut_math_5 ?? 0).toBeGreaterThanOrEqual(40);
  });

  it('picks multi-part hard items for bagrut_math_5', () => {
    const items = pickExamStyleItems({
      goalKey: 'bagrut_math_5',
      conceptIds: ['derivatives_rules', 'definite_integrals'],
      count: 3,
      rotation: 0,
    });
    expect(items.length).toBe(3);
    for (const it of items) {
      expect(it.parts.length).toBeGreaterThanOrEqual(2);
      expect(it.stem_he.length).toBeGreaterThan(20);
      expect(it.source).toBe('asf_original');
    }
  });

  it('formats stem with parts for display', () => {
    const [it] = pickExamStyleItems({ goalKey: 'bagrut_math_5', count: 1 });
    expect(it).toBeTruthy();
    const stem = formatExamStyleStem(it!, 'he');
    expect(stem).toContain('**(');
  });

  it('rotates selections', () => {
    const a = pickExamStyleItems({ goalKey: 'bagrut_math_4', count: 3, rotation: 0 });
    const b = pickExamStyleItems({ goalKey: 'bagrut_math_4', count: 3, rotation: 3 });
    expect(a.map((x) => x.id).join()).not.toBe(b.map((x) => x.id).join());
  });
});
