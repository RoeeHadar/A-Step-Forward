import { describe, expect, it } from 'vitest';
import {
  filterAdultGoals,
  filterGoalsForLearner,
  needsUniversityPicker,
  yearsGapLabelForSubject,
} from './onboarding-options';

describe('needsUniversityPicker', () => {
  it('shows for pre-university and university grades only', () => {
    expect(
      needsUniversityPicker({
        gradeLevel: '12',
        isAdultLearner: false,
        adultGoal: '',
      }),
    ).toBe(false);
    expect(
      needsUniversityPicker({
        gradeLevel: 'pre_university',
        isAdultLearner: false,
        adultGoal: '',
      }),
    ).toBe(true);
  });

  it('does not show for HS even when adult picks uni course elsewhere', () => {
    expect(
      needsUniversityPicker({
        gradeLevel: '11',
        isAdultLearner: false,
        adultGoal: 'university_math',
      }),
    ).toBe(false);
  });

  it('shows for adult learner with university goal', () => {
    expect(
      needsUniversityPicker({
        gradeLevel: 'adult_learner',
        isAdultLearner: true,
        adultGoal: 'university_physics',
      }),
    ).toBe(true);
  });
});

describe('filterGoalsForLearner', () => {
  it('limits HS grade 10 to bagrut goals for chosen subjects', () => {
    expect(
      filterGoalsForLearner({ gradeLevel: '10', subjects: ['physics'] }),
    ).toEqual(['bagrut_physics', 'other']);
    expect(
      filterGoalsForLearner({ gradeLevel: '10', subjects: ['math', 'physics'] }),
    ).toEqual([
      'bagrut_math_5',
      'bagrut_math_4',
      'bagrut_math_3',
      'bagrut_physics',
      'other',
    ]);
  });

  it('offers university math goals for pre-university math students', () => {
    expect(
      filterGoalsForLearner({ gradeLevel: 'pre_university', subjects: ['math'] }),
    ).toEqual(['calculus1', 'linear_algebra', 'university_prep', 'other']);
  });
});

describe('filterAdultGoals', () => {
  it('returns subject-specific adult goals', () => {
    expect(filterAdultGoals(['math'])).toEqual([
      'bagrut_math',
      'university_math',
      'general_improvement',
    ]);
    expect(filterAdultGoals(['physics'])).toEqual([
      'bagrut_physics',
      'university_physics',
      'general_improvement',
    ]);
  });
});

describe('yearsGapLabelForSubject', () => {
  it('uses subject-specific wording', () => {
    expect(yearsGapLabelForSubject('physics', 'en')).toContain('physics');
    expect(yearsGapLabelForSubject('math', 'en')).toContain('math');
  });
});
