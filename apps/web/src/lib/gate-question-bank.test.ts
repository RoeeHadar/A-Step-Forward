import { describe, expect, it } from 'vitest';
import {
  GATE_BANK_FORMAT_VERSION,
  isBankSourcedGateQuiz,
  pickGateQuestionsFromBank,
  scoreLessonQuestionForGate,
} from './gate-question-bank';

describe('pickGateQuestionsFromBank', () => {
  it('returns hard/open/numeric-heavy items for well-covered concepts', () => {
    const picks = pickGateQuestionsFromBank({
      conceptIds: ['derivatives_rules', 'algebra_basics'],
      locale: 'he',
      count: 6,
      rotation: 0,
      preferHard: true,
    });
    expect(picks.length).toBeGreaterThanOrEqual(4);
    expect(picks.every((p) => p.source === 'lesson_bank')).toBe(true);
    expect(picks.every((p) => p.format_version === GATE_BANK_FORMAT_VERSION)).toBe(true);
    const recognition = picks.filter((p) => p.kind === 'mcq' || p.kind === 'true_false').length;
    expect(recognition).toBeLessThanOrEqual(Math.max(1, Math.floor(6 * 0.25)));
    const productive = picks.filter((p) =>
      ['open', 'derivation', 'numeric', 'short_answer'].includes(p.kind),
    );
    expect(productive.length).toBeGreaterThanOrEqual(picks.length - recognition);
  });

  it('rotates items across retakes', () => {
    const a = pickGateQuestionsFromBank({
      conceptIds: ['logarithms', 'factoring'],
      locale: 'en',
      count: 5,
      rotation: 0,
    });
    const b = pickGateQuestionsFromBank({
      conceptIds: ['logarithms', 'factoring'],
      locale: 'en',
      count: 5,
      rotation: 1,
    });
    expect(a.length).toBeGreaterThan(0);
    expect(b.length).toBeGreaterThan(0);
    const idsA = a.map((p) => p.id).join(',');
    const idsB = b.map((p) => p.id).join(',');
    // Not a hard guarantee of total difference, but rotations should not be identical.
    expect(idsA === idsB).toBe(false);
  });
});

describe('scoreLessonQuestionForGate', () => {
  it('ranks open/hard above easy mcq', () => {
    const openHard = scoreLessonQuestionForGate({ kind: 'open', difficulty: 'hard' });
    const easyMcq = scoreLessonQuestionForGate({ kind: 'mcq', difficulty: 'easy' });
    expect(openHard).toBeGreaterThan(easyMcq);
  });
});

describe('isBankSourcedGateQuiz', () => {
  it('accepts v2 format and rejects legacy mcq-only caches', () => {
    expect(
      isBankSourcedGateQuiz([
        { source: 'lesson_bank', format_version: GATE_BANK_FORMAT_VERSION, kind: 'numeric' },
        { source: 'llm_fallback', format_version: GATE_BANK_FORMAT_VERSION, kind: 'open' },
      ]),
    ).toBe(true);
    expect(
      isBankSourcedGateQuiz([
        { kind: 'mcq' },
        { kind: 'mcq' },
        { kind: 'mcq' },
      ]),
    ).toBe(false);
  });
});
