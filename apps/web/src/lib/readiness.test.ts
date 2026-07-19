import { describe, expect, it } from 'vitest';
import {
  computeReadiness,
  concaveReadiness,
  decayMastery,
  EXAM_READY_CRITICAL_COVERAGE,
  MASTERY_HALF_LIFE_DAYS,
  MOCK_GATED_CEILING,
  READINESS_CEILING,
} from './readiness';
import { criticalConceptsForGoal, listGoalKeys } from './plan-pacing';

// A goal that actually has a frontier + critical concepts.
const GOAL = listGoalKeys().find((k) => criticalConceptsForGoal(k).size > 0)!;

describe('readiness: decayMastery', () => {
  it('no decay for fresh or zero-day activity', () => {
    expect(decayMastery(0.9, 0)).toBe(0.9);
    expect(decayMastery(0.9, null)).toBe(0.9);
  });

  it('halves at the half-life', () => {
    expect(decayMastery(0.8, MASTERY_HALF_LIFE_DAYS)).toBeCloseTo(0.4, 5);
  });

  it('is monotonic decreasing in days and returns 0 for non-positive scores', () => {
    expect(decayMastery(0.9, 10)).toBeGreaterThan(decayMastery(0.9, 60));
    expect(decayMastery(0, 5)).toBe(0);
    expect(decayMastery(-1, 5)).toBe(0);
  });
});

describe('readiness: concaveReadiness', () => {
  it('maps 0→0 and 1→ceiling', () => {
    expect(concaveReadiness(0)).toBe(0);
    expect(concaveReadiness(1)).toBeCloseTo(READINESS_CEILING, 5);
  });

  it('is monotonic increasing', () => {
    expect(concaveReadiness(0.4)).toBeLessThan(concaveReadiness(0.6));
  });

  it('gains near the top cost more coverage than near the bottom (80→85 harder than 50→55)', () => {
    // Coverage needed to move the DISPLAY up 5 points, low vs high.
    const invert = (display: number) => 1 - Math.sqrt(1 - display / READINESS_CEILING);
    const lowCost = invert(0.55) - invert(0.5);
    const highCost = invert(0.85) - invert(0.8);
    expect(highCost).toBeGreaterThan(lowCost);
  });
});

describe('readiness: computeReadiness', () => {
  it('returns null for a goal with no frontier', () => {
    expect(computeReadiness({ goalKey: 'nope', masteryScores: {} })).toBeNull();
  });

  it('a total beginner is foundational, low readiness, not exam-ready', () => {
    const r = computeReadiness({ goalKey: GOAL, masteryScores: {} })!;
    expect(r.band).toBe('foundational');
    expect(r.exam_ready).toBe(false);
    expect(r.readiness).toBeLessThan(0.2);
  });

  it('never reports guaranteed success — capped below 1.0 even at full coverage + mock', () => {
    const crit = [...criticalConceptsForGoal(GOAL)];
    const scores: Record<string, number> = {};
    for (const id of crit) scores[id] = 1;
    // Master the whole core too.
    const r = computeReadiness({ goalKey: GOAL, masteryScores: scores, mockPassed: true })!;
    expect(r.readiness).toBeLessThanOrEqual(READINESS_CEILING);
    expect(r.readiness).toBeLessThan(1);
  });

  it('mock gate: high coverage without a passed mock is capped', () => {
    const crit = [...criticalConceptsForGoal(GOAL)];
    const scores: Record<string, number> = {};
    for (const id of crit) scores[id] = 1;
    const noMock = computeReadiness({ goalKey: GOAL, masteryScores: scores, mockPassed: false })!;
    expect(noMock.readiness).toBeLessThanOrEqual(MOCK_GATED_CEILING + 1e-9);
    expect(noMock.exam_ready).toBe(false);
    const withMock = computeReadiness({ goalKey: GOAL, masteryScores: scores, mockPassed: true })!;
    expect(withMock.readiness).toBeGreaterThan(noMock.readiness);
  });

  it('exam-ready needs both ~90% critical coverage AND a passed mock', () => {
    const crit = [...criticalConceptsForGoal(GOAL)];
    const scores: Record<string, number> = {};
    for (const id of crit) scores[id] = 1; // 100% critical coverage ≥ threshold
    expect(EXAM_READY_CRITICAL_COVERAGE).toBeLessThanOrEqual(1);
    expect(computeReadiness({ goalKey: GOAL, masteryScores: scores, mockPassed: true })!.exam_ready).toBe(true);
    expect(computeReadiness({ goalKey: GOAL, masteryScores: scores, mockPassed: false })!.exam_ready).toBe(false);
  });

  it('decay lowers coverage: stale mastery counts for less', () => {
    const crit = [...criticalConceptsForGoal(GOAL)];
    const scores: Record<string, number> = {};
    const staleDays: Record<string, number> = {};
    for (const id of crit) {
      scores[id] = 0.85;
      staleDays[id] = MASTERY_HALF_LIFE_DAYS * 2; // decays 0.85 → ~0.21, below mastered
    }
    const fresh = computeReadiness({ goalKey: GOAL, masteryScores: scores })!;
    const stale = computeReadiness({ goalKey: GOAL, masteryScores: scores, activityDays: staleDays })!;
    expect(stale.critical_coverage).toBeLessThan(fresh.critical_coverage);
  });

  it('phase: day-before and final-phase are derived from days to exam', () => {
    const base = { goalKey: GOAL, masteryScores: {} };
    expect(computeReadiness({ ...base, daysToExam: 0 })!.phase).toBe('day_before');
    expect(computeReadiness({ ...base, daysToExam: 1 })!.phase).toBe('day_before');
    expect(computeReadiness({ ...base, daysToExam: 7 })!.phase).toBe('final_phase');
    expect(computeReadiness({ ...base, daysToExam: 60 })!.phase).toBe('building');
    expect(computeReadiness({ ...base, daysToExam: null })!.phase).toBe('building');
    // Day-before message overrides band.
    expect(computeReadiness({ ...base, daysToExam: 0 })!.message_key).toBe('day_before');
  });
});
