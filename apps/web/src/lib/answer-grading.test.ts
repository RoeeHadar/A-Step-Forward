import { describe, expect, it } from 'vitest';
import {
  coerceBooleanAnswer,
  coerceOptionIndex,
  getAcceptedAnswers,
  resolveCorrectBool,
} from './answer-normalize';

/** Mirrors neon-db gradeLessonAnswer true_false branch (no Neon import). */
function gradeTrueFalse(
  payload: unknown,
  userAnswer: unknown,
  correctAnswer?: string | null,
): boolean {
  const expected = resolveCorrectBool(payload, { correct_answer: correctAnswer });
  const picked = coerceBooleanAnswer(userAnswer);
  if (picked == null || expected == null) return false;
  return picked === expected;
}

describe('answer grading coercion', () => {
  it('coerces string correct_index', () => {
    expect(coerceOptionIndex('0')).toBe(0);
    expect(coerceOptionIndex(2)).toBe(2);
  });

  it('coerces string correct_bool via resolveCorrectBool', () => {
    expect(resolveCorrectBool({ correct_bool: 'true' })).toBe(true);
    expect(gradeTrueFalse({ correct_bool: 'true' }, true)).toBe(true);
  });

  it('grades true_false from answer_payload.value (seed alias)', () => {
    expect(gradeTrueFalse({ value: true }, true)).toBe(true);
    expect(gradeTrueFalse({ value: true }, false)).toBe(false);
  });

  it('grades true_false from answer_payload.correct (seed alias)', () => {
    expect(gradeTrueFalse({ correct: false }, false)).toBe(true);
  });

  it('resolveCorrectBool prefers correct_bool then value then correct', () => {
    expect(resolveCorrectBool({ correct_bool: true, value: false })).toBe(true);
    expect(resolveCorrectBool({ value: false })).toBe(false);
    expect(resolveCorrectBool({ correct: true })).toBe(true);
    expect(resolveCorrectBool({}, { correct_answer: 'true' })).toBe(true);
    expect(resolveCorrectBool(null)).toBeNull();
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
