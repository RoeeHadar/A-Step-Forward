import { describe, expect, it } from 'vitest';
import {
  DIAGNOSTIC_QUESTIONS_PER_SESSION,
  normalizeLearnerSubjects,
  resolveDiagnosticPointsLevel,
} from './diagnostic-start';
import { isTemplateDiagnosticStem } from './neon-db';

describe('DIAGNOSTIC_QUESTIONS_PER_SESSION', () => {
  it('is six focused validation questions per run', () => {
    expect(DIAGNOSTIC_QUESTIONS_PER_SESSION).toBe(6);
  });
});

describe('isTemplateDiagnosticStem', () => {
  it('flags KG bootstrap placeholder stems', () => {
    expect(isTemplateDiagnosticStem('Which statement best describes **Foo**?')).toBe(true);
    expect(isTemplateDiagnosticStem('איזה משפט מתאר בצורה הטובה ביותר **בעיות קיצון**?')).toBe(
      true,
    );
    expect(isTemplateDiagnosticStem('Find the derivative of $x^2$.')).toBe(false);
  });
});

describe('normalizeLearnerSubjects', () => {
  it('returns math when subjects missing or empty', () => {
    expect(normalizeLearnerSubjects(null)).toEqual(['math']);
    expect(normalizeLearnerSubjects([])).toEqual(['math']);
  });

  it('keeps valid math/physics selections', () => {
    expect(normalizeLearnerSubjects(['physics'])).toEqual(['physics']);
    expect(normalizeLearnerSubjects(['math', 'physics'])).toEqual(['math', 'physics']);
  });
});

describe('resolveDiagnosticPointsLevel', () => {
  it('reads points_group pt suffix', () => {
    expect(resolveDiagnosticPointsLevel({ pointsGroup: '4pt' })).toBe('4pt');
    expect(resolveDiagnosticPointsLevel({ pointsGroup: '5' })).toBe('5pt');
  });

  it('ignores hs_physics points group', () => {
    expect(resolveDiagnosticPointsLevel({ pointsGroup: 'hs_physics' })).toBeNull();
  });

  it('uses goal_key instead of substring heuristics on free text', () => {
    expect(
      resolveDiagnosticPointsLevel({
        goalKey: 'bagrut_math_5',
        pointsGroup: null,
      }),
    ).toBe('5pt');
    expect(
      resolveDiagnosticPointsLevel({
        goalKey: 'linear_algebra',
        pointsGroup: null,
      }),
    ).toBeNull();
  });
});
