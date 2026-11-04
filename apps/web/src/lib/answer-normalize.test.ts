import { describe, expect, it } from 'vitest';
import {
  answerText,
  answersMatch,
  coerceBooleanAnswer,
  displayCorrectAnswer,
  getAcceptedAnswers,
  normalizeAnswerForGrading,
  numericClose,
  resolveCorrectBool,
} from './answer-normalize';

describe('answer-normalize', () => {
  it('strips LaTeX delimiters and normalizes case', () => {
    expect(normalizeAnswerForGrading('$x^2$')).toBe('x^2');
    expect(normalizeAnswerForGrading('  Hello  ')).toBe('hello');
  });

  it('matches answers with LaTeX wrappers', () => {
    const accepted = getAcceptedAnswers(['x^2'], 'x^2');
    expect(answersMatch('$x^2$', accepted)).toBe(true);
  });

  it('falls back to correct_answer when acceptable_answers are garbage', () => {
    const accepted = getAcceptedAnswers(['==', '[[TODO]]'], '42');
    expect(accepted).toEqual(['42']);
    expect(answersMatch('42', accepted)).toBe(true);
  });

  it('displayCorrectAnswer prefers correct_answer field', () => {
    expect(displayCorrectAnswer(['wrong template'], '7')).toBe('7');
  });

  it('numericClose tolerates small formatting differences', () => {
    expect(numericClose('$3.14$', '3.14')).toBe(true);
    expect(numericClose('3.141', '3.14')).toBe(true);
  });

  it('numericClose grades tiny scientific-notation answers strictly', () => {
    // Photon energy: 0 must NOT be accepted for 6.6e-19 J.
    expect(numericClose('0', '6.6e-19')).toBe(false);
    expect(numericClose('6.6e-19', '6.6e-19')).toBe(true);
    expect(numericClose('6.7e-19', '6.6e-19')).toBe(true); // within 5%
    expect(numericClose('8e-19', '6.6e-19')).toBe(false); // >5% off
    // Exact-zero answers still match a typed zero.
    expect(numericClose('0', '0')).toBe(true);
  });

  // Regression: seed/bundle data stored correct_answer as JSON numbers or
  // booleans, and `.trim()` on them crashed lesson pages with a 500.
  describe('non-string correct_answer', () => {
    // Data arrives untyped from JSON, so cast past the declared string type.
    const asAnswer = (v: unknown) => v as string;

    it('resolveCorrectBool does not throw on numeric or boolean correct_answer', () => {
      expect(() => resolveCorrectBool(undefined, { correct_answer: asAnswer(15) })).not.toThrow();
      expect(() => resolveCorrectBool(undefined, { correct_answer: asAnswer(true) })).not.toThrow();
      expect(() => resolveCorrectBool({ kind: 'x' }, { correct_answer: asAnswer(3.14) })).not.toThrow();
    });

    it('resolveCorrectBool still scores booleans correctly', () => {
      expect(resolveCorrectBool(undefined, { correct_answer: asAnswer(true) })).toBe(true);
      expect(resolveCorrectBool(undefined, { correct_answer: asAnswer(false) })).toBe(false);
      expect(resolveCorrectBool(undefined, { correct_answer: asAnswer(1) })).toBe(true);
      expect(resolveCorrectBool(undefined, { correct_answer: asAnswer(0) })).toBe(false);
      expect(resolveCorrectBool(undefined, { correct_answer: asAnswer(15) })).toBeNull();
      // String forms behave exactly as before.
      expect(resolveCorrectBool(undefined, { correct_answer: ' True ' })).toBe(true);
      expect(resolveCorrectBool(undefined, { correct_answer: 'no' })).toBe(false);
      expect(resolveCorrectBool(undefined, { correct_answer: null })).toBeNull();
      // Payload still wins over the fallback.
      expect(resolveCorrectBool({ correct: false }, { correct_answer: asAnswer(true) })).toBe(false);
    });

    it('numeric answers still grade right and wrong', () => {
      expect(numericClose('15', asAnswer(15))).toBe(true);
      expect(numericClose('16', asAnswer(15))).toBe(false);
      expect(numericClose('3.1416', asAnswer(3.14159))).toBe(true);
      const accepted = getAcceptedAnswers([], asAnswer(42));
      expect(accepted).toEqual(['42']);
      expect(answersMatch('42', accepted)).toBe(true);
      expect(answersMatch('41', accepted)).toBe(false);
      expect(displayCorrectAnswer(undefined, asAnswer(7))).toBe('7');
    });

    it('accepts Hebrew true/false in the stored key and in the submission', () => {
      // Stored key (correct_answer fallback).
      expect(resolveCorrectBool(undefined, { correct_answer: 'נכון' })).toBe(true);
      expect(resolveCorrectBool(undefined, { correct_answer: ' לא נכון ' })).toBe(false);
      expect(resolveCorrectBool(undefined, { correct_answer: 'לא  נכון' })).toBe(false);
      expect(resolveCorrectBool(undefined, { correct_answer: 'נָכוֹן' })).toBe(true);
      expect(resolveCorrectBool(undefined, { correct_answer: 'לֹא נָכוֹן' })).toBe(false);
      expect(resolveCorrectBool({ value: 'לא נכון' }, {})).toBe(false);
      // Student submission.
      expect(coerceBooleanAnswer('נכון')).toBe(true);
      expect(coerceBooleanAnswer('  נכון\n')).toBe(true);
      expect(coerceBooleanAnswer('לא נכון')).toBe(false);
      expect(coerceBooleanAnswer('לא\tנכון')).toBe(false);
      expect(coerceBooleanAnswer('נָכוֹן')).toBe(true);
      // Not true/false words.
      expect(coerceBooleanAnswer('נכון חלקית')).toBeNull();
      // maqaf / hyphen between the words (Orchestrator, 28 Oct)
      expect(coerceBooleanAnswer('לא\u05BEנכון')).toBe(false);
      expect(coerceBooleanAnswer('לא-נכון')).toBe(false);
      expect(coerceBooleanAnswer('לא – נכון')).toBe(false);
      expect(coerceBooleanAnswer('לֹא\u05BEנָכוֹן')).toBe(false);
      expect(resolveCorrectBool(undefined, { correct_answer: 'לא\u05BEנכון' })).toBe(false);
      expect(coerceBooleanAnswer('נכון-חלקית')).toBeNull();
      expect(coerceBooleanAnswer('לא')).toBeNull();
      expect(resolveCorrectBool(undefined, { correct_answer: 'נכון חלקית' })).toBeNull();
      // English behaviour unchanged.
      expect(coerceBooleanAnswer('true')).toBe(true);
      expect(coerceBooleanAnswer(' true ')).toBeNull();
    });

    it('answerText coerces safely', () => {
      expect(answerText(12.5)).toBe('12.5');
      expect(answerText(false)).toBe('false');
      expect(answerText('  x ')).toBe('x');
      expect(answerText(null)).toBe('');
      expect(answerText(undefined)).toBe('');
      expect(answerText({})).toBe('');
    });
  });
});
