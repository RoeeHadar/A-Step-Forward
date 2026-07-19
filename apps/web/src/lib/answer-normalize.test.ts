import { describe, expect, it } from 'vitest';
import {
  answersMatch,
  displayCorrectAnswer,
  getAcceptedAnswers,
  normalizeAnswerForGrading,
  numericClose,
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
});
