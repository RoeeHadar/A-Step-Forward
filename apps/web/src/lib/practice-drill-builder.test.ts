import { describe, expect, it } from 'vitest';
import { buildHintLadder, isPracticeArenaKind, stemLooksLanguageMixed } from './practice-arena';

/** Local mirror of open-first validate rules (no LLM). */
function validateOpenShape(raw: {
  kind: string;
  stem_en: string;
  stem_he: string;
  model_answer_en?: string;
  correct_answer?: string;
}): boolean {
  if (!isPracticeArenaKind(raw.kind)) return false;
  if (raw.kind === 'mcq' || raw.kind === 'true_false') return false;
  if (raw.stem_en.length < 12 || raw.stem_he.length < 12) return false;
  if (stemLooksLanguageMixed(raw.stem_en) || stemLooksLanguageMixed(raw.stem_he)) return false;
  if (raw.kind === 'open') return Boolean(raw.model_answer_en);
  return Boolean(raw.correct_answer);
}

describe('practice-drill-builder validation helpers (v2 open)', () => {
  it('accepts well-formed open shapes', () => {
    expect(
      validateOpenShape({
        kind: 'open',
        stem_en: 'Prove the derivative of x^2 using first principles.',
        stem_he: 'הוכיחו את נגזרת x^2 מההגדרה עם גבול.',
        model_answer_en: 'Use lim h->0 ...',
      }),
    ).toBe(true);
  });

  it('rejects mcq for the open-first arena', () => {
    expect(
      validateOpenShape({
        kind: 'mcq',
        stem_en: 'What is the power rule for x^n here?',
        stem_he: 'מהו כלל החזקה עבור x^n כאן עכשיו?',
      }),
    ).toBe(false);
  });

  it('hint ladder stays answer-free even with leaky explanations passed through', () => {
    const hints = buildHintLadder({
      conceptLabelEn: 'Derivatives',
      conceptLabelHe: 'נגזרות',
      skillAtoms: ['power_rule'],
      explanationEn: 'The answer is 2x.',
      explanationHe: 'התשובה היא 2x.',
    });
    const text = hints.map((h) => `${h.en} ${h.he}`).join(' ');
    expect(text).not.toContain('2x');
    expect(text).not.toContain('The answer is');
  });
});
