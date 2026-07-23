import { describe, expect, it } from 'vitest';
import {
  buildHintLadder,
  isPracticeArenaKind,
  isPracticeExamWorthyItem,
  practiceQuestionIdLooksBoilerplate,
  stemLooksLanguageMixed,
  stemLooksVagueOrMeta,
} from './practice-arena';

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
  if (stemLooksVagueOrMeta(raw.stem_en) || stemLooksVagueOrMeta(raw.stem_he)) return false;
  if (
    !isPracticeExamWorthyItem({
      stemEn: raw.stem_en,
      stemHe: raw.stem_he,
      explanationEn: raw.model_answer_en,
      explanationHe: raw.model_answer_en,
    })
  ) {
    return false;
  }
  if (raw.kind === 'open') return Boolean(raw.model_answer_en);
  return Boolean(raw.correct_answer);
}

describe('practice-drill-builder validation helpers (v2 open)', () => {
  it('accepts well-formed open shapes', () => {
    expect(
      validateOpenShape({
        kind: 'open',
        stem_en: 'Prove the derivative of $x^2$ using first principles.',
        stem_he: 'הוכיחו את נגזרת $x^2$ מההגדרה עם גבול.',
        model_answer_en: 'Use lim h->0 of ( (x+h)^2 - x^2 ) / h = 2x.',
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

  it('rejects vague meta stems about f(x)=k without concrete f', () => {
    expect(
      stemLooksVagueOrMeta(
        'מהגרף של y=f(x) (או מנוסחה מפורשת אם ניתנה בשיעור), הסבירו כמה פתרונות יכולה להיות למשוואה f(x)=k כשהישר האופקי y=k זז.',
      ),
    ).toBe(true);
    expect(
      stemLooksVagueOrMeta(
        'עבור $f(x)=x^2-4x$ מצאו את ערכי $k$ שעבורם למשוואה $f(x)=k$ יש שני פתרונות שונים.',
      ),
    ).toBe(false);
  });

  it('rejects lesson-facet pedagogical boilerplate', () => {
    expect(
      stemLooksVagueOrMeta(
        'יישמו את פני השיעור (expression_structure, error_analysis): תנו דוגמה פתורה קצרה.',
      ),
    ).toBe(true);
    expect(practiceQuestionIdLooksBoilerplate('algebra_basics-facet-auto')).toBe(true);
    expect(
      isPracticeExamWorthyItem({
        stemEn: 'Apply the lesson facets (expression_structure): give a short worked example.',
        stemHe: 'יישמו את פני השיעור (expression_structure): תנו דוגמה פתורה קצרה.',
        explanationEn: '**Facet drill.** Identify which facet applies…',
        explanationHe: '**תרגול פנים.** זהו איזה פן חל…',
        questionId: 'algebra_basics-facet-auto',
      }),
    ).toBe(false);
    expect(
      isPracticeExamWorthyItem({
        stemEn:
          'A square of side $a+b$ has area $(a+b)^2$. Expand and explain what $2ab$ means geometrically.',
        stemHe:
          'לריבוע צלע $a+b$ יש שטח $(a+b)^2$. פתחו את השטח והסבירו מה מייצג $2ab$ גאומטרית.',
        explanationEn: 'Expand to $a^2+2ab+b^2$; the middle term is two rectangles.',
        explanationHe: '$(a+b)^2=a^2+2ab+b^2$ — איבר האמצע הוא שני מלבנים.',
        questionId: 'algebra_basics-q3',
      }),
    ).toBe(true);
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
