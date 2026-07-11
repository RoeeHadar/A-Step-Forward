export type OnboardingSubject = 'math' | 'physics';

export type OnboardingGoal =
  | 'bagrut_math_5'
  | 'bagrut_math_4'
  | 'bagrut_math_3'
  | 'bagrut_physics'
  | 'calculus1'
  | 'linear_algebra'
  | 'university_prep'
  | 'other';

export type AdultGoal =
  | 'bagrut_math'
  | 'bagrut_physics'
  | 'university_math'
  | 'university_physics'
  | 'general_improvement';

export const HS_BAGRUT_GRADES = new Set(['10', '11', '12', 'adult_bagrut']);

export const UNIVERSITY_GRADE_LEVELS = new Set([
  'pre_university',
  'university_1',
  'university_2plus',
]);

const MATH_BAGRUT_GOALS: OnboardingGoal[] = [
  'bagrut_math_5',
  'bagrut_math_4',
  'bagrut_math_3',
];

const UNIVERSITY_MATH_GOALS: OnboardingGoal[] = [
  'calculus1',
  'linear_algebra',
  'university_prep',
];

export function isUniversityGradeLevel(gradeLevel: string): boolean {
  return UNIVERSITY_GRADE_LEVELS.has(gradeLevel);
}

export function isHighSchoolGradeLevel(gradeLevel: string): boolean {
  return HS_BAGRUT_GRADES.has(gradeLevel);
}

/** University picker only for pre-uni / uni tracks — never for grades 10–12. */
export function needsUniversityPicker(input: {
  gradeLevel: string;
  isAdultLearner: boolean;
  adultGoal: string;
}): boolean {
  if (isUniversityGradeLevel(input.gradeLevel)) return true;
  if (
    input.isAdultLearner &&
    (input.adultGoal === 'university_math' || input.adultGoal === 'university_physics')
  ) {
    return true;
  }
  return false;
}

export function filterGoalsForLearner(input: {
  gradeLevel: string;
  subjects: OnboardingSubject[];
}): OnboardingGoal[] {
  const { gradeLevel, subjects } = input;
  const hasMath = subjects.includes('math');
  const hasPhysics = subjects.includes('physics');
  const goals: OnboardingGoal[] = [];

  if (isUniversityGradeLevel(gradeLevel)) {
    if (hasMath) goals.push(...UNIVERSITY_MATH_GOALS);
    if (hasPhysics) goals.push('bagrut_physics');
  } else if (isHighSchoolGradeLevel(gradeLevel)) {
    if (hasMath) goals.push(...MATH_BAGRUT_GOALS);
    if (hasPhysics) goals.push('bagrut_physics');
  }

  goals.push('other');
  return goals;
}

export function filterAdultGoals(subjects: OnboardingSubject[]): AdultGoal[] {
  const hasMath = subjects.includes('math');
  const hasPhysics = subjects.includes('physics');
  const goals: AdultGoal[] = [];
  if (hasMath) {
    goals.push('bagrut_math', 'university_math');
  }
  if (hasPhysics) {
    goals.push('bagrut_physics', 'university_physics');
  }
  if (hasMath || hasPhysics) {
    goals.push('general_improvement');
  }
  return goals;
}

export function yearsGapLabelForSubject(
  subject: OnboardingSubject,
  lang: 'en' | 'he',
): string {
  if (subject === 'physics') {
    return lang === 'he'
      ? 'כמה זמן עבר מאז שלמדת פיזיקה?'
      : 'How long since you last studied physics?';
  }
  return lang === 'he'
    ? 'כמה זמן עבר מאז שלמדת מתמטיקה?'
    : 'How long since you last studied math?';
}

export function subjectLabel(subject: OnboardingSubject, lang: 'en' | 'he'): string {
  if (subject === 'math') return lang === 'he' ? 'מתמטיקה' : 'Math';
  return lang === 'he' ? 'פיזיקה' : 'Physics';
}
