import { describe, expect, it } from 'vitest';
import {
  conceptInPlanScope,
  conceptMatchesSubjects,
  masterySignalInScope,
  resolveConceptSubject,
} from './concept-scope';

describe('concept-scope', () => {
  it('resolves lesson-index ids to their subject', () => {
    expect(resolveConceptSubject('sequences_5pt')).toBe('math');
    expect(resolveConceptSubject('kinematics_1d')).toBe('physics');
  });

  it('excludes math lesson mastery for physics-only learners', () => {
    expect(conceptMatchesSubjects('sequences_5pt', ['physics'])).toBe(false);
    expect(conceptMatchesSubjects('kinematics_1d', ['physics'])).toBe(true);
  });

  it('defaults unknown ids to out-of-scope for subject filter', () => {
    expect(conceptMatchesSubjects('totally_unknown_xyz', ['physics'])).toBe(false);
  });

  it('scopes mastery signals to active plan concepts when a plan exists', () => {
    const planConceptIds = new Set(['kinematics_1d', 'circular_motion']);
    expect(
      masterySignalInScope('sequences_5pt', {
        subjects: ['physics'],
        planConceptIds,
      }),
    ).toBe(false);
    expect(
      masterySignalInScope('kinematics_1d', {
        subjects: ['physics'],
        planConceptIds,
      }),
    ).toBe(true);
  });

  it('falls back to subject filter when no plan concepts exist', () => {
    expect(
      masterySignalInScope('kinematics_1d', {
        subjects: ['physics'],
        planConceptIds: new Set(),
      }),
    ).toBe(true);
    expect(
      masterySignalInScope('sequences_5pt', {
        subjects: ['physics'],
        planConceptIds: new Set(),
      }),
    ).toBe(false);
  });

  it('matches plan scope across aliases and canonical ids', () => {
    const planConceptIds = new Set(['circular_motion']);
    expect(conceptInPlanScope('circular_motion', planConceptIds)).toBe(true);
  });
});
