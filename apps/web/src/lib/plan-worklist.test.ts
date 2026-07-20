import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  buildFastPlanConceptOrder,
  buildUnifiedPlanConceptOrder,
  chunkConceptsIntoWeeks,
  DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY,
  resolveGoalConceptId,
  ROLLING_VISIBLE_WEEKS,
} from './plan-worklist';
import { getFrontier } from './plan-pacing';

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
    expect(ordered.length).toBeGreaterThan(0);
    // Frontier-anchored selection is preferred over BFS for goals with a manifest.
    expect(mockBuildLearningPlan).not.toHaveBeenCalled();
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

describe('buildFastPlanConceptOrder', () => {
  beforeEach(() => {
    mockBuildLearningPlan.mockReset();
  });

  it('orders from weak mastery and diagnostic priority without BFS', () => {
    const ordered = buildFastPlanConceptOrder({
      profile: {
        ...baseProfile,
        self_scores: { limits: 0.3, algebra_basics: 0.4 },
      },
      mastery: { limits: 0.25, algebra_basics: 0.35 },
      options: {
        prependConcepts: ['functions_quadratic'],
        priorityConcepts: ['limits'],
        excludeConcepts: [],
      },
    });

    expect(ordered[0]).toBe('functions_quadratic');
    expect(ordered).toContain('limits');
    expect(mockBuildLearningPlan).not.toHaveBeenCalled();
  });

  it('falls back to self_scores keys when mastery worklist is empty', () => {
    const ordered = buildFastPlanConceptOrder({
      profile: {
        subjects: ['math'],
        self_scores: { limits: 0.5, algebra_basics: 0.6 },
        personality_profile: null,
      },
      mastery: {},
    });

    expect(ordered.length).toBeGreaterThan(0);
    expect(ordered).toContain('limits');
  });

  it('anchors bagrut_math_5 mid-mastery away from 3pt foundations', () => {
    const frontier = getFrontier('bagrut_math_5')!;
    const criticalIds = frontier.core.filter((c) => c.critical).map((c) => c.id);
    const nonCritical = frontier.core.filter((c) => !c.critical).map((c) => c.id);
    const nMasterCritical = Math.floor(criticalIds.length * 0.82);
    const mastered = [
      ...criticalIds.slice(0, nMasterCritical),
      ...nonCritical.slice(0, 8),
    ];
    const mastery = Object.fromEntries(mastered.map((id) => [id, 0.88]));

    const ordered = buildFastPlanConceptOrder({
      profile: baseProfile,
      mastery,
    });

    expect(ordered.length).toBeGreaterThan(0);
    expect(ordered).not.toContain('quadrilaterals');
    expect(ordered).not.toContain('arithmetic');
    const depthById = new Map(frontier.core.map((c) => [c.id, c.depth]));
    for (const id of ordered.slice(0, 4)) {
      expect(depthById.get(id)!).toBeGreaterThanOrEqual(7);
    }
    expect(mockBuildLearningPlan).not.toHaveBeenCalled();
  });
});

describe('chunkConceptsIntoWeeks', () => {
  it('fills week 1 then week 2 sequentially (not round-robin)', () => {
    const groups = chunkConceptsIntoWeeks(
      ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
      ROLLING_VISIBLE_WEEKS,
      4,
    );
    expect(groups).toHaveLength(2);
    expect(groups[0]).toEqual(['a', 'b', 'c', 'd']);
    expect(groups[1]).toEqual(['e', 'f', 'g', 'h']);
  });

  it('caps to visible weeks × per-week', () => {
    const groups = chunkConceptsIntoWeeks(['a', 'b'], 2, 4);
    expect(groups[0]).toEqual(['a', 'b']);
    expect(groups[1]).toEqual([]);
  });
});
