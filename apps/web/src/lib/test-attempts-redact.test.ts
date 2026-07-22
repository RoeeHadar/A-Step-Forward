import { describe, expect, it } from 'vitest';
import { redactQuestionsUntilGraded } from './test-attempt-redact';

const sample = [
  {
    id: 'q1',
    topic: 'math',
    subject: 'math',
    stem: '2+2?',
    options: [
      { key: 'A', text: '3' },
      { key: 'B', text: '4' },
    ],
    correct: 'B',
    model_answer: '4',
    rubric: 'Award full credit for 4',
  },
];

describe('redactQuestionsUntilGraded', () => {
  it('keeps keys when grading is complete', () => {
    const q = redactQuestionsUntilGraded(sample, 'complete')[0]!;
    expect(q.correct).toBe('B');
    expect(q.model_answer).toBe('4');
    expect(q.rubric).toBe('Award full credit for 4');
  });

  it('strips correct/model_answer/rubric while pending/grading/failed', () => {
    for (const status of ['pending', 'grading', 'failed', 'needs_human', 'reopened'] as const) {
      const q = redactQuestionsUntilGraded(sample, status)[0]!;
      expect(q.correct).toBe('');
      expect(q).not.toHaveProperty('model_answer');
      expect(q).not.toHaveProperty('rubric');
      expect(q.stem).toBe('2+2?');
      expect(q.options).toEqual(sample[0]!.options);
    }
  });
});

/** Mirrors mapListRow reveal rules for educators (scores visible before release). */
function revealAttemptScores(
  gradingStatus: string,
  forEducator: boolean,
  score: number | null,
  passed: boolean | null,
) {
  const complete = gradingStatus === 'complete';
  const reveal = complete || forEducator;
  return {
    score: reveal ? score : null,
    passed: reveal ? passed : null,
  };
}

describe('educator attempt score visibility', () => {
  it('hides provisional score from learners while needs_human', () => {
    expect(revealAttemptScores('needs_human', false, 0.6, false)).toEqual({
      score: null,
      passed: null,
    });
  });

  it('shows provisional score to educators while needs_human', () => {
    expect(revealAttemptScores('needs_human', true, 0.6, false)).toEqual({
      score: 0.6,
      passed: false,
    });
  });

  it('shows released score to both', () => {
    expect(revealAttemptScores('complete', false, 0.9, true)).toEqual({
      score: 0.9,
      passed: true,
    });
    expect(revealAttemptScores('complete', true, 0.9, true)).toEqual({
      score: 0.9,
      passed: true,
    });
  });
});
