import { describe, expect, it } from 'vitest';
import {
  assessQuizQuestionSolvability,
  filterSolvableQuizQuestions,
  partAsksDiagonalBisectionProof,
  stemEstablishesParallelogramFamily,
} from './quiz-solvability';

describe('assessQuizQuestionSolvability — real failure from pilot', () => {
  const badPilotItem = {
    stem_he:
      'במרובע ABCD, אורך הצלע AB הוא 8 ס"מ ואורך הצלע AD הוא 10 ס"מ. הגובה של המרובע הוא 6 ס"מ.',
    stem_en:
      'In quadrilateral ABCD, AB = 8 cm and AD = 10 cm. The height of the quadrilateral is 6 cm.',
    parts: [
      {
        label: 'א',
        body_he: 'מצא את שטח המרובע.',
        body_en: 'Find the area of the quadrilateral.',
        points: 8,
      },
      {
        label: 'ב',
        body_he: 'הוכח שהאלכסונים של המרובע חוצים זה את זה.',
        body_en: 'Prove that the diagonals of the quadrilateral bisect each other.',
        points: 8,
      },
      {
        label: 'ג',
        body_he: 'אם המרובע הוא מלבן, מצא את אורך האלכסון.',
        body_en: 'If the quadrilateral is a rectangle, find the length of the diagonal.',
        points: 9,
      },
    ],
    sample_solution_he:
      'חלק א: שטח = בסיס × גובה. חלק ב: לא ניתן להוכיח, חסרים נתונים.',
    sample_solution_en:
      'Part A: area = base × height. Part B: cannot prove — insufficient data.',
  };

  it('rejects the unsolvable diagonal-bisection + ambiguous-area item', () => {
    const result = assessQuizQuestionSolvability(badPilotItem);
    expect(result.ok).toBe(false);
    expect(result.reasons).toContain('diagonal_bisection_without_parallelogram');
    expect(result.reasons).toContain('ambiguous_quadrilateral_area');
    expect(result.reasons).toContain('solution_admits_insufficient_data');
  });

  it('filterSolvableQuizQuestions drops the bad item', () => {
    const { kept, dropped } = filterSolvableQuizQuestions([badPilotItem]);
    expect(kept).toHaveLength(0);
    expect(dropped).toHaveLength(1);
  });
});

describe('assessQuizQuestionSolvability — valid parallelogram item', () => {
  it('keeps a well-posed parallelogram proof', () => {
    const good = {
      stem_he: 'במקבילית ABCD נתון AB = 8, הגובה לצלע AB הוא 6.',
      stem_en: 'In parallelogram ABCD, AB = 8 and the height to side AB is 6.',
      parts: [
        {
          label: 'א',
          body_he: 'מצא את שטח המקבילית.',
          body_en: 'Find the area of the parallelogram.',
        },
        {
          label: 'ב',
          body_he: 'הוכח שהאלכסונים חוצים זה את זה.',
          body_en: 'Prove that the diagonals bisect each other.',
        },
      ],
      sample_solution_he:
        'חלק א: שטח = 8 × 6 = 48. חלק ב: במקבילית האלכסונים חוצים זה את זה לפי הגדרה/משפט — הוכחה באמצעות משולשים חופפים.',
      sample_solution_en:
        'Part A: area = 8 × 6 = 48. Part B: in a parallelogram the diagonals bisect each other by the standard congruent-triangles proof.',
    };
    const result = assessQuizQuestionSolvability(good);
    expect(result.ok).toBe(true);
    expect(result.reasons).toHaveLength(0);
  });
});

describe('helpers', () => {
  it('detects parallelogram family in stem', () => {
    expect(stemEstablishesParallelogramFamily('In parallelogram ABCD…')).toBe(true);
    expect(stemEstablishesParallelogramFamily('במרובע ABCD…')).toBe(false);
  });

  it('detects diagonal-bisection proof asks', () => {
    expect(
      partAsksDiagonalBisectionProof('הוכח שהאלכסונים של המרובע חוצים זה את זה'),
    ).toBe(true);
    expect(partAsksDiagonalBisectionProof('מצא את אורך האלכסון')).toBe(false);
  });
});
