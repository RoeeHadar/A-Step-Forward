import { describe, expect, it } from 'vitest';
import { deriveOnboardingSeedScores, resolveSelfScoreConceptIds } from './onboarding-self-score';

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

describe('deriveOnboardingSeedScores', () => {
  it('builds neutral scores from goal when self_scores empty', () => {
    const scores = deriveOnboardingSeedScores({
      goal: 'bagrut_math_5',
      subjects: ['math'],
      grade_level: '12',
      points_group: '5',
      personality_profile: { goal_key: 'bagrut_math_5' },
    });
    expect(Object.keys(scores).length).toBeGreaterThan(0);
    expect(scores.limits).toBe(5);
  });

  it('preserves provided self_scores', () => {
    const scores = deriveOnboardingSeedScores({
      goal: 'bagrut_math_5',
      subjects: ['math'],
      self_scores: { limits: 3 },
    });
    expect(scores).toEqual({ limits: 3 });
  });
});
