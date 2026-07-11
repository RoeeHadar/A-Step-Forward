import { describe, expect, it } from 'vitest';
import {
  applyDiagnosticResponse,
  buildDiagnosticSummary,
  buildValidationQueue,
  emptyDiagnosticSession,
  isDiagnosticSessionComplete,
  nextCatDifficulty,
  orderProbeConcepts,
  selfScoreTier,
  validationDifficultyForSelfScore,
} from './diagnostic-plan';
import { DIAGNOSTIC_QUESTIONS_PER_SESSION } from './diagnostic-start';
import { stemAllowedForProfile } from './diagnostic-stem-filter';

describe('validationDifficultyForSelfScore', () => {
  it('maps weak self-score to basic items', () => {
    expect(validationDifficultyForSelfScore(2)).toBeLessThan(validationDifficultyForSelfScore(9));
  });
  it('maps strong self-score to hard validation', () => {
    expect(validationDifficultyForSelfScore(9)).toBeGreaterThanOrEqual(8);
  });
});

describe('selfScoreTier', () => {
  it('classifies weak, ok, and strong bands', () => {
    expect(selfScoreTier(3)).toBe('weak');
    expect(selfScoreTier(6)).toBe('ok');
    expect(selfScoreTier(9)).toBe('strong');
  });
});

describe('buildValidationQueue', () => {
  it('always produces 12 slots with two probes per concept tier', () => {
    const queue = buildValidationQueue(
      ['linear_functions', 'quadratic_equations', 'derivatives_intro'],
      { linear_functions: 3, quadratic_equations: 6, derivatives_intro: 9 },
      DIAGNOSTIC_QUESTIONS_PER_SESSION,
    );
    expect(queue).toHaveLength(12);
    expect(queue.filter((s) => s.concept_id === 'linear_functions').length).toBeGreaterThanOrEqual(2);
    expect(queue.find((s) => s.concept_id === 'linear_functions')?.slot_kind).toBe('basic');
    expect(queue.find((s) => s.concept_id === 'derivatives_intro')?.slot_kind).toBe('hard');
  });
});

describe('isDiagnosticSessionComplete', () => {
  it('requires all validation slots before completion', () => {
    const queue = buildValidationQueue(['linear_functions'], { linear_functions: 5 }, 12);
    let state = emptyDiagnosticSession('function_analysis_4pt', ['linear_functions'], queue);
    expect(isDiagnosticSessionComplete(state)).toBe(false);
    state = applyDiagnosticResponse(state, {
      item_id: 'a',
      topic: 'linear_functions',
      difficulty: 5,
      correct: true,
      chosen: 'A',
    });
    expect(isDiagnosticSessionComplete(state)).toBe(false);
  });
});

describe('nextCatDifficulty', () => {
  it('raises difficulty after correct answer', () => {
    expect(nextCatDifficulty(5, true)).toBeGreaterThan(5);
  });
  it('lowers difficulty after wrong answer', () => {
    expect(nextCatDifficulty(5, false)).toBeLessThan(5);
  });
});

describe('orderProbeConcepts', () => {
  it('prioritizes weak self-scores before path order', () => {
    const ordered = orderProbeConcepts(
      ['linear_functions', 'quadratic_equations', 'derivatives_intro'],
      { linear_functions: 3, quadratic_equations: 8 },
      12,
    );
    expect(ordered[0]).toBe('linear_functions');
    expect(ordered).toContain('derivatives_intro');
  });
});

describe('buildDiagnosticSummary', () => {
  it('produces agent brief and plan focus from responses', () => {
    const queue = buildValidationQueue(
      ['linear_functions', 'quadratic_equations'],
      { linear_functions: 3, quadratic_equations: 8 },
      2,
    );
    let state = emptyDiagnosticSession('function_analysis_4pt', [
      'linear_functions',
      'quadratic_equations',
    ], queue);
    state = applyDiagnosticResponse(state, {
      item_id: 'a',
      topic: 'linear_functions',
      difficulty: 4,
      correct: false,
      chosen: 'A',
    });
    state = applyDiagnosticResponse(state, {
      item_id: 'b',
      topic: 'quadratic_equations',
      difficulty: 6,
      correct: true,
      chosen: 'B',
    });
    const summary = buildDiagnosticSummary(state, new Date('2026-07-11T12:00:00Z'));
    expect(summary.weak_concepts).toContain('linear_functions');
    expect(summary.agent_brief_en).toMatch(/calibration/i);
    expect(summary.plan_focus_concepts.length).toBeGreaterThan(0);
  });
});

describe('stemAllowedForProfile', () => {
  it('blocks real-number field notation for 4pt high school', () => {
    const profile = { points_group: '4pt', subjects: ['math'] } as never;
    expect(stemAllowedForProfile('Let f: ℝ → ℝ be a function', profile)).toBe(false);
    expect(stemAllowedForProfile('What is the slope of y = 2x + 1?', profile)).toBe(true);
  });
});
