/** Map onboarding grade values to the curriculum routing key. */
export function effectiveGradeLevel(grade: string | null | undefined): string | null {
  if (!grade) return null;
  if (grade === 'adult_bagrut') return '12';
  return grade;
}
