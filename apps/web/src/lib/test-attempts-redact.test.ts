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
  },
];

describe('redactQuestionsUntilGraded', () => {
  it('keeps keys when grading is complete', () => {
    expect(redactQuestionsUntilGraded(sample, 'complete')[0]?.correct).toBe('B');
  });

  it('strips keys while pending/grading/failed', () => {
    for (const status of ['pending', 'grading', 'failed'] as const) {
      expect(redactQuestionsUntilGraded(sample, status)[0]?.correct).toBe('');
    }
  });
});
