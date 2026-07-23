import { describe, expect, it } from 'vitest';
import { buildHintLadder, isPracticeClosedKind } from './practice-arena';

/** Local mirror of validate rules used by the drill builder (no LLM). */
function validateShape(raw: {
  kind: string;
  stem_en: string;
  stem_he: string;
  correct_index?: number;
  options_en?: string[];
  options_he?: string[];
}): boolean {
  if (!isPracticeClosedKind(raw.kind)) return false;
  if (raw.stem_en.length < 8 || raw.stem_he.length < 8) return false;
  if (raw.kind === 'mcq') {
    return (
      (raw.options_en?.length ?? 0) >= 3 &&
      (raw.options_he?.length ?? 0) >= 3 &&
      typeof raw.correct_index === 'number' &&
      raw.correct_index >= 0
    );
  }
  return true;
}

describe('practice-drill-builder validation helpers', () => {
  it('accepts well-formed MCQ shapes', () => {
    expect(
      validateShape({
        kind: 'mcq',
        stem_en: 'What is the power rule for x^n?',
        stem_he: 'מהו כלל החזקה עבור x^n?',
        options_en: ['a', 'b', 'c', 'd'],
        options_he: ['א', 'ב', 'ג', 'ד'],
        correct_index: 0,
      }),
    ).toBe(true);
  });

  it('rejects open / unknown kinds', () => {
    expect(
      validateShape({
        kind: 'open',
        stem_en: 'Prove something long enough',
        stem_he: 'הוכח משהו באורך מספיק',
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
