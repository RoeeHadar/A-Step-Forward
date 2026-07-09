import { describe, expect, it } from 'vitest';
import {
  bootstrapConceptIdsForProfile,
  conceptAllowedForProfile,
  filterConceptIdsForProfile,
} from './quiz-concept-filter';

describe('quiz-concept-filter', () => {
  it('filters physics-only learners away from calc-only concepts', () => {
    const profile = {
      subjects: ['physics'],
      points_group: 'hs_physics',
    } as Parameters<typeof conceptAllowedForProfile>[1];

    expect(conceptAllowedForProfile('kinematics_1d', profile)).toBe(true);
    expect(conceptAllowedForProfile('linear_algebra_basics', profile)).toBe(false);
  });

  it('bootstrap respects learner subjects', () => {
    const profile = {
      subjects: ['physics'],
      points_group: 'hs_physics',
    } as Parameters<typeof bootstrapConceptIdsForProfile>[0];

    const ids = bootstrapConceptIdsForProfile(profile, 6);
    expect(ids.length).toBeGreaterThan(0);
    for (const id of ids) {
      expect(conceptAllowedForProfile(id, profile)).toBe(true);
    }
  });

  it('filterConceptIdsForProfile drops out-of-scope ids', () => {
    const profile = {
      subjects: ['physics'],
      points_group: 'hs_physics',
    } as Parameters<typeof filterConceptIdsForProfile>[1];

    const filtered = filterConceptIdsForProfile(
      ['kinematics_1d', 'linear_algebra_basics', 'not_a_concept'],
      profile,
    );
    expect(filtered).toContain('kinematics_1d');
    expect(filtered).not.toContain('linear_algebra_basics');
  });
});
