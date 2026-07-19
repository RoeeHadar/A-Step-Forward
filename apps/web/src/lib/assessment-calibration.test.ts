/**
 * ADR-0010 Stream F — calibration / ground-truth guardrails.
 *
 * These tests pin the numeric behavior the assessment-driven progression relies on,
 * so a future parameter tweak (pass threshold, critical floor, decay half-life,
 * readiness curve) can't silently change gating or readiness semantics. They are the
 * lightweight, deterministic stand-in for the fuller promptfoo/DeepEval calibration
 * harness (deferred): the gate decision, readiness bands and decay are pure, so we can
 * assert them against an explicit ground-truth matrix.
 */
import { describe, expect, it } from 'vitest';
import {
  criticalConceptsForGoal,
  evaluateGatePass,
  GATE_AGGREGATE_THRESHOLD,
  GATE_CRITICAL_FLOOR,
  listGoalKeys,
} from './plan-pacing';
import { computeReadiness, decayMastery, MASTERY_HALF_LIFE_DAYS } from './readiness';

const GOAL = listGoalKeys().find((k) => criticalConceptsForGoal(k).size > 0)!;
const CRIT = [...criticalConceptsForGoal(GOAL)];

describe('calibration: weekly-gate ground truth', () => {
  const c0 = CRIT[0]!;
  const c1 = CRIT[1] ?? CRIT[0]!;

  // [name, aggregate, per-critical scores, expected pass]
  const matrix: Array<[string, number, Record<string, number>, boolean]> = [
    ['clear pass — high aggregate, criticals above floor', 0.9, { [c0]: 0.8, [c1]: 0.7 }, true],
    ['exact thresholds pass', GATE_AGGREGATE_THRESHOLD, { [c0]: GATE_CRITICAL_FLOOR }, true],
    ['aggregate just below threshold fails', GATE_AGGREGATE_THRESHOLD - 0.01, { [c0]: 0.9 }, false],
    ['critical just below floor fails despite strong aggregate', 0.95, { [c0]: GATE_CRITICAL_FLOOR - 0.01 }, false],
    ['no criticals assessed → aggregate-only pass', 0.8, { some_other: 0.1 }, true],
    ['both fail', 0.4, { [c0]: 0.2 }, false],
  ];

  for (const [name, aggregate, perTopic, expected] of matrix) {
    it(name, () => {
      expect(evaluateGatePass({ aggregateScore: aggregate, perTopic, goalKey: GOAL }).passed).toBe(
        expected,
      );
    });
  }
});

describe('calibration: decay half-life', () => {
  it('score halves exactly at the half-life and quarters at 2x', () => {
    expect(decayMastery(1, MASTERY_HALF_LIFE_DAYS)).toBeCloseTo(0.5, 6);
    expect(decayMastery(1, MASTERY_HALF_LIFE_DAYS * 2)).toBeCloseTo(0.25, 6);
  });
});

describe('calibration: readiness bands & mock gate', () => {
  function withCoverage(fraction: number, mockPassed: boolean) {
    // Master the first `fraction` of critical concepts.
    const n = Math.round(CRIT.length * fraction);
    const scores: Record<string, number> = {};
    for (let i = 0; i < n; i += 1) scores[CRIT[i]!] = 1;
    return computeReadiness({ goalKey: GOAL, masteryScores: scores, mockPassed })!;
  }

  it('readiness is monotonic non-decreasing in coverage', () => {
    const points = [0, 0.25, 0.5, 0.75, 1].map((f) => withCoverage(f, true).readiness);
    for (let i = 1; i < points.length; i += 1) {
      expect(points[i]!).toBeGreaterThanOrEqual(points[i - 1]!);
    }
  });

  it('a passed mock strictly raises readiness at high coverage', () => {
    expect(withCoverage(1, true).readiness).toBeGreaterThan(withCoverage(1, false).readiness);
  });

  it('full coverage + mock is exam-ready but never 100%', () => {
    const r = withCoverage(1, true);
    expect(r.exam_ready).toBe(true);
    expect(r.readiness).toBeLessThan(1);
  });

  it('full coverage without a mock is never exam-ready', () => {
    expect(withCoverage(1, false).exam_ready).toBe(false);
  });
});
