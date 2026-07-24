import { describe, expect, it } from 'vitest';
import {
  goalCountdownLabel,
  isBagrutTrack,
  readinessTitle,
} from './goal-track';
import {
  clipHorizonWeeks,
  clipMaterializedWeeks,
  filterWeekGroupsBeforeGoal,
} from './plan-horizon';
import {
  computePlanMode,
  fractionTimeUsed,
  lessonTrainSplit,
  phaseFromFraction,
  trainTargetCount,
} from './plan-mode';
import {
  buildWeekWorkItems,
  encodeWorkItem,
  parseWorkItemToken,
  conceptIdsFromWorkItems,
} from './plan-work-items';
import {
  countStrongPracticeSignals,
  shouldPromoteTrainDominant,
} from './plan-train-signals';
import {
  computeReadiness,
  NO_PRACTICE_CEILING,
  MOCK_GATED_CEILING,
} from './readiness';

describe('goal-track', () => {
  it('detects bagrut vs uni calc', () => {
    expect(isBagrutTrack({ goalKey: 'bagrut_math_5' })).toBe(true);
    expect(isBagrutTrack({ goalKey: 'calculus1', goal: 'מבחן בחדו״א 1' })).toBe(false);
    expect(isBagrutTrack({ goal: 'בגרות מתמטיקה' })).toBe(true);
  });

  it('does not frame calc1 as bagrut when goal_key is stale', () => {
    expect(
      isBagrutTrack({ goalKey: 'bagrut_math_5', goal: 'מבחן בחדו״א 1' }),
    ).toBe(false);
    expect(
      isBagrutTrack({ goalKey: 'bagrut_math_5', goal: 'מבחן בחדוא 1' }),
    ).toBe(false);
    expect(
      goalCountdownLabel('he', 6, {
        isBagrut: isBagrutTrack({
          goalKey: 'bagrut_math_5',
          goal: 'מבחן בחדו״א 1',
        }),
      }),
    ).not.toContain('בגרות');
  });

  it('countdown labels avoid bagrut for uni goals', () => {
    expect(goalCountdownLabel('he', 6, { isBagrut: false })).toContain('יעד');
    expect(goalCountdownLabel('he', 6, { isBagrut: false })).not.toContain('בגרות');
    expect(goalCountdownLabel('he', 6, { isBagrut: true })).toContain('בגרות');
    expect(readinessTitle('he', { isBagrut: false })).toBe('מוכנות ליעד');
  });
});

describe('plan-mode phases', () => {
  it('maps fraction to lesson / train / rest', () => {
    expect(phaseFromFraction(0.5, 20)).toBe('lesson_heavy');
    expect(phaseFromFraction(0.85, 10)).toBe('train_heavy');
    expect(phaseFromFraction(0.97, 5)).toBe('rest');
    expect(phaseFromFraction(0.5, 1)).toBe('rest');
  });

  it('computes train-dominant from readiness near exam or behavior', () => {
    expect(
      computePlanMode({ daysToGoal: 7, readiness: 0.8, phase: 'lesson_heavy' }),
    ).toBe('train_dominant');
    expect(
      computePlanMode({
        daysToGoal: 30,
        readiness: 0.4,
        strongPracticeSignals: 2,
        phase: 'lesson_heavy',
      }),
    ).toBe('train_dominant');
    expect(
      computePlanMode({ daysToGoal: 40, readiness: 0.4, phase: 'lesson_heavy' }),
    ).toBe('lessons_and_train');
  });

  it('splits lesson vs train slots', () => {
    expect(
      lessonTrainSplit(4, 'lessons_and_train', 'lesson_heavy').lessons,
    ).toBeGreaterThan(lessonTrainSplit(4, 'train_dominant', 'train_heavy').lessons);
    expect(trainTargetCount('train_dominant', 'train_heavy')).toBe(12);
    expect(
      fractionTimeUsed({
        planStartIso: '2026-07-01',
        goalDeadlineIso: '2026-07-31',
        now: new Date('2026-07-16T12:00:00'),
      }),
    ).toBeGreaterThan(0.4);
  });
});

describe('plan-work-items', () => {
  it('round-trips encode/parse and bare ids stay lessons', () => {
    expect(parseWorkItemToken('limits')).toEqual({ kind: 'lesson', concept_id: 'limits' });
    expect(parseWorkItemToken('train:limits:12')).toEqual({
      kind: 'train',
      concept_id: 'limits',
      target_count: 12,
    });
    expect(encodeWorkItem({ kind: 'train', concept_id: 'limits', target_count: 8 })).toBe(
      'train:limits:8',
    );
    expect(parseWorkItemToken('rest').kind).toBe('rest');
  });

  it('builds week items with train rows', () => {
    const items = buildWeekWorkItems(
      ['a', 'b', 'c', 'd'],
      'lessons_and_train',
      'lesson_heavy',
    );
    expect(items.some((i) => i.kind === 'lesson')).toBe(true);
    expect(conceptIdsFromWorkItems(items).length).toBeGreaterThan(0);
  });
});

describe('plan-horizon', () => {
  it('clips materialized weeks near the goal', () => {
    expect(clipMaterializedWeeks({ daysToGoal: 5, requestedWeeks: 2 })).toBe(1);
    expect(clipMaterializedWeeks({ daysToGoal: 40, requestedWeeks: 2 })).toBe(2);
    expect(clipHorizonWeeks({ daysToGoal: 10, horizonWeeks: 8 })).toBe(2);
  });

  it('filters week groups after goal', () => {
    const kept = filterWeekGroupsBeforeGoal(
      [['a'], ['b'], ['c']],
      '2026-07-20',
      '2026-07-25',
    );
    expect(kept.length).toBeLessThan(3);
  });
});

describe('practice dampening on readiness', () => {
  it('caps readiness with zero skills practiced', () => {
    const r = computeReadiness({
      goalKey: 'bagrut_math_5',
      masteryScores: Object.fromEntries(
        Array.from({ length: 40 }, (_, i) => [`concept_${i}`, 0.95]),
      ),
      mockPassed: false,
      skillsPracticedCount: 0,
      daysToExam: 14,
    });
    if (!r) return;
    expect(r.readiness).toBeLessThanOrEqual(NO_PRACTICE_CEILING + 1e-9);
    expect(r.readiness).toBeLessThanOrEqual(MOCK_GATED_CEILING + 1e-9);
  });
});

describe('train behavior signals', () => {
  it('promotes train-dominant after enough strong signals', () => {
    const n = countStrongPracticeSignals(
      ['limits', 'derivatives'],
      {
        limits: { attempts: 5, successes: 4 },
        derivatives: { attempts: 4, successes: 3 },
      },
    );
    expect(n).toBe(2);
    expect(shouldPromoteTrainDominant(n)).toBe(true);
    expect(shouldPromoteTrainDominant(1)).toBe(false);
  });
});
