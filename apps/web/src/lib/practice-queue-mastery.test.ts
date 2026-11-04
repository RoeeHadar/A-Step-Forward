/** AS-54 (C5c): practice difficulty selected from the mastery estimate (BKT flag) via advancePracticeItem. */
import { describe, it, expect, vi } from 'vitest';
vi.mock('server-only', () => ({}));
vi.mock('@/lib/practice-drill-builder', () => ({ buildPracticeDrillItem: vi.fn(async () => null) }));
import { practiceDifficultyFromMastery, bktReplay } from '@/lib/bkt';
import { nextDifficulty } from '@/lib/practice-arena';
import { advancePracticeItem } from '@/lib/practice-queue';

const base = { learnerId: 'u-test', conceptFilter: 'functions_quadratic', queueMode: 'default' as const, seenIds: [], generatedCount: 0, previousDifficulty: 'medium' as const };

describe('practiceDifficultyFromMastery', () => {
  it('bands the BKT estimate', () => {
    expect(practiceDifficultyFromMastery([])).toBeNull();
    expect(practiceDifficultyFromMastery([false, false, false])).toBe('easy');
    expect(practiceDifficultyFromMastery([true, true, true])).toBe('hard');
    expect(bktReplay([true])).toBeGreaterThan(0.2);
    expect(practiceDifficultyFromMastery([true])).toBe('medium');
    expect(practiceDifficultyFromMastery([true, false, true, false])).toBe('medium');
  });
});

describe('advancePracticeItem difficulty (real selection path)', { timeout: 60_000 }, () => {
  it('bkt: J1 three wrong lowers to easy and serves an easy item', async () => {
    const r = await advancePracticeItem({ ...base, recentCorrect: [false, false, false], masteryModel: 'bkt' });
    expect(r && 'item' in r && r.difficulty).toBe('easy');
    expect(r && 'item' in r && r.item.difficulty).toBe('easy');
  });
  it('bkt: J2 strong raises to hard and serves a hard item', async () => {
    const r = await advancePracticeItem({ ...base, recentCorrect: [true, true, true], masteryModel: 'bkt' });
    expect(r && 'item' in r && r.difficulty).toBe('hard');
    expect(r && 'item' in r && r.item.difficulty).toBe('hard');
  });
  it('bkt: no attempts keeps the current difficulty', async () => {
    const r = await advancePracticeItem({ ...base, recentCorrect: [], masteryModel: 'bkt' });
    expect(r && 'item' in r && r.difficulty).toBe('medium');
  });
  it('ratio (flag unset) target equals the pre-AS-54 nextDifficulty rule', async () => {
    for (const seq of [[], [true], [false, false], [true, true, true], [true, false, true]]) {
      const r = await advancePracticeItem({ ...base, recentCorrect: seq });
      expect(r && 'item' in r && r.difficulty).toBe(nextDifficulty(seq, 'medium'));
    }
  });
});
