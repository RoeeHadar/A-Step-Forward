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
    for (const status of ['pending', 'grading', 'failed'] as const) {
      const q = redactQuestionsUntilGraded(sample, status)[0]!;
      expect(q.correct).toBe('');
      expect(q).not.toHaveProperty('model_answer');
      expect(q).not.toHaveProperty('rubric');
      expect(q.stem).toBe('2+2?');
    }
  });
});
