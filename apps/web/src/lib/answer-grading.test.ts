import { describe, expect, it } from 'vitest';
import {
  coerceBooleanAnswer,
  coerceOptionIndex,
  getAcceptedAnswers,
} from './answer-normalize';
import { gradeLessonAnswer } from './neon-db';

describe('answer grading coercion', () => {
  it('coerces string correct_index from Postgres JSON', () => {
    expect(coerceOptionIndex('0')).toBe(0);
    expect(coerceOptionIndex(2)).toBe(2);
    expect(
      gradeLessonAnswer(
        { kind: 'mcq', correct_index: '1' as unknown as number, correct_answer: null, answer_payload: null },
        1,
        undefined,
      ).correct,
    ).toBe(true);
  });

  it('coerces string correct_bool', () => {
    expect(
      gradeLessonAnswer(
        {
          kind: 'true_false',
          correct_index: null,
          correct_answer: null,
          answer_payload: { correct_bool: 'true' as unknown as boolean },
        },
        true,
        undefined,
      ).correct,
    ).toBe(true);
  });

  it('extracts concise answers from polluted acceptable_answers seeds', () => {
    const accepted = getAcceptedAnswers(
      [
        '**Solution:**\n\n$x^2-16$.\n\n**Check:** Re-substitute',
        '-16',
      ],
      null,
    );
    expect(accepted.some((a) => a.includes('x^2-16'))).toBe(true);
  });

  it('coerces boolean strings', () => {
    expect(coerceBooleanAnswer('false')).toBe(false);
    expect(coerceBooleanAnswer('true')).toBe(true);
  });
});
