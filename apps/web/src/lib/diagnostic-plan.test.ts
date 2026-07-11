import { describe, expect, it } from 'vitest';
import {
  applyDiagnosticResponse,
  buildDiagnosticSummary,
  emptyDiagnosticSession,
  nextCatDifficulty,
  orderProbeConcepts,
  selfScoreToDifficulty,
} from './diagnostic-plan';

describe('selfScoreToDifficulty', () => {
  it('maps low self-score to easier items', () => {
    expect(selfScoreToDifficulty(2)).toBeLessThan(selfScoreToDifficulty(8));
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
    let state = emptyDiagnosticSession('function_analysis_4pt', [
      'linear_functions',
      'quadratic_equations',
    ]);
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
    expect(summary.agent_brief_en).toMatch(/Diagnostic/i);
    expect(summary.plan_focus_concepts.length).toBeGreaterThan(0);
  });
});
