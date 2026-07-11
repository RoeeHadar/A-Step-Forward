import { describe, expect, it } from 'vitest';
import { resolveSelfScoreConceptIds } from './onboarding-self-score';

describe('resolveSelfScoreConceptIds', () => {
  it('uses foundational math for Bagrut 3pt', () => {
    const ids = resolveSelfScoreConceptIds({
      goal: 'bagrut_math_3',
      isAdultLearner: false,
      subjects: ['math'],
      gradeLevel: '11',
      pointsGroup: '3',
    });
    expect(ids).toContain('arithmetic');
    expect(ids).toContain('algebra_basics');
    expect(ids).not.toContain('la_eigenvalues');
  });

  it('includes physics basics for physics-only HS', () => {
    const ids = resolveSelfScoreConceptIds({
      goal: 'bagrut_physics',
      isAdultLearner: false,
      subjects: ['physics'],
      gradeLevel: '12',
      pointsGroup: '',
    });
    expect(ids).toContain('kinematics_1d');
    expect(ids).toContain('newton_laws');
  });
});
