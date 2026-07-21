import { describe, expect, it } from 'vitest';
import {
  gradingUiPhaseSealed,
  isAttemptReleased,
  isAttemptSealed,
  sealGradingViewForClient,
  settleOpenOutcome,
} from './sealed-attempt-visibility';

describe('sealed-attempt-visibility', () => {
  it('releases only on complete', () => {
    expect(isAttemptReleased('complete')).toBe(true);
    expect(isAttemptReleased('pending')).toBe(false);
    expect(isAttemptReleased('needs_human')).toBe(false);
    expect(isAttemptSealed('needs_human')).toBe(true);
  });

  it('seals marks until release', () => {
    const sealed = sealGradingViewForClient({
      grading_status: 'pending',
      score: 0.9,
      passed: true,
      per_topic: { a: 1 },
      weak_concepts: ['x'],
      item_feedback: { q1: { status: 'graded' } },
      item_scores: { q1: 1 },
    });
    expect(sealed.score).toBeNull();
    expect(sealed.passed).toBeNull();
    expect(sealed.item_feedback).toEqual({});
    expect(sealed.item_scores).toEqual({});

    const open = sealGradingViewForClient({
      grading_status: 'complete',
      score: 0.9,
      passed: true,
      per_topic: { a: 1 },
      weak_concepts: ['x'],
      item_feedback: { q1: { status: 'graded' } },
      item_scores: { q1: 1 },
    });
    expect(open.score).toBe(0.9);
    expect(open.item_scores.q1).toBe(1);
  });

  it('settles to needs_human when an open permanently fails', () => {
    expect(
      settleOpenOutcome(
        ['a', 'b'],
        {
          a: { status: 'graded', retries: 0 },
          b: { status: 'failed', retries: 3 },
        },
        3,
      ),
    ).toBe('needs_human');
  });

  it('settles to release when all opens graded', () => {
    expect(
      settleOpenOutcome(
        ['a'],
        { a: { status: 'graded', retries: 0 } },
        3,
      ),
    ).toBe('release');
  });

  it('maps UI phase for needs_human', () => {
    expect(gradingUiPhaseSealed({ grading_status: 'needs_human' })).toBe('needs_human');
    expect(gradingUiPhaseSealed({ grading_status: 'complete', score: 0.5 })).toBe(
      'complete',
    );
  });
});
