import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  buildUnifiedPlanConceptOrder,
  DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY,
  resolveGoalConceptId,
} from './plan-worklist';

const mockBuildLearningPlan = vi.fn();

vi.mock('./learning-plan', () => ({
  buildLearningPlan: (...args: unknown[]) => mockBuildLearningPlan(...args),
}));

const baseProfile = {
  subjects: ['math'],
  self_scores: null,
  personality_profile: { goal_key: 'bagrut_math_5' },
};

describe('resolveGoalConceptId', () => {
  it('picks priority concept over goal_key default', () => {
    const goal = resolveGoalConceptId(
      baseProfile,
      {},
      { priorityConcepts: ['limits'], prependConcepts: [] },
    );
    expect(goal).toBe('limits');
    expect(DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY.bagrut_math_5).toBe('function_analysis_5pt');
  });

  it('falls back to goal_key default when no priority or prepend', () => {
    const goal = resolveGoalConceptId(baseProfile, {});
    expect(goal).toBe('function_analysis_asymptotes');
  });
});

describe('buildUnifiedPlanConceptOrder', () => {
  beforeEach(() => {
    mockBuildLearningPlan.mockReset();
    mockBuildLearningPlan.mockResolvedValue({
      goal: { concept_id: 'derivatives_intro', name: 'Derivatives', name_he: null, subject: 'math' },
      path: [
        { concept_id: 'limits', relation: 'prereq' },
        { concept_id: 'algebra_basics', relation: 'prereq' },
        { concept_id: 'derivatives_intro', relation: 'self' },
      ],
      blocking_atoms: [],
      generated_at: new Date().toISOString(),
    });
  });

  it('merges prepend concepts before path order', async () => {
    const ordered = await buildUnifiedPlanConceptOrder({
      learnerId: 'learner-1',
      profile: baseProfile,
      mastery: {},
      options: {
        prependConcepts: ['functions_quadratic'],
        priorityConcepts: [],
        excludeConcepts: [],
      },
      numWeeks: 4,
    });

    expect(ordered[0]).toBe('functions_quadratic');
    expect(ordered).toContain('limits');
    expect(ordered.indexOf('functions_quadratic')).toBeLessThan(ordered.indexOf('limits'));
    expect(mockBuildLearningPlan).toHaveBeenCalled();
  });

  it('focusConceptsOnly filters to prepend and priority set', async () => {
    const ordered = await buildUnifiedPlanConceptOrder({
      learnerId: 'learner-1',
      profile: baseProfile,
      mastery: {},
      options: {
        prependConcepts: ['limits'],
        priorityConcepts: ['algebra_basics'],
        excludeConcepts: [],
        focusConceptsOnly: true,
      },
      numWeeks: 4,
    });

    expect(ordered).toEqual(['limits', 'algebra_basics']);
    expect(ordered).not.toContain('derivatives_intro');
  });
});
