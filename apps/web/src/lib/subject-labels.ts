/** Human-readable labels for Learning Database subject slugs. */
export const SUBJECT_LABELS: Record<string, { en: string; he: string; icon: string }> = {
  'hs-math-3': { en: 'High School Math — 3pt', he: 'מתמטיקה — 3 יח״ל', icon: '3' },
  'math-hs-3': { en: 'High School Math — 3pt', he: 'מתמטיקה — 3 יח״ל', icon: '3' },
  hs_math_3: { en: 'High School Math — 3pt', he: 'מתמטיקה — 3 יח״ל', icon: '3' },
  'hs-math-4': { en: 'High School Math — 4pt', he: 'מתמטיקה — 4 יח״ל', icon: '4' },
  hs_math_4: { en: 'High School Math — 4pt', he: 'מתמטיקה — 4 יח״ל', icon: '4' },
  'hs-math-5': { en: 'High School Math — 5pt', he: 'מתמטיקה — 5 יח״ל', icon: '5' },
  hs_math_5: { en: 'High School Math — 5pt', he: 'מתמטיקה — 5 יח״ל', icon: '5' },
  hs_physics: { en: 'Physics', he: 'פיזיקה', icon: '⚛️' },
  math: { en: 'Mathematics', he: 'מתמטיקה', icon: '📐' },
  physics: { en: 'Physics', he: 'פיזיקה', icon: '⚛️' },
  calculus: { en: 'Calculus', he: 'חדו״א', icon: '∫' },
  calculus_1: { en: 'Calculus 1', he: 'חדו״א 1', icon: '∫' },
  linear_algebra: { en: 'Linear Algebra', he: 'אלגברה לינארית', icon: '⎡' },
  statistics_probability: { en: 'Statistics & Probability', he: 'סטטיסטיקה והסתברות', icon: '📊' },
  math_pre_university: { en: 'Math Pre-University', he: 'מתמטיקה לפני אוניברסיטה', icon: '🧮' },
  middle_school_math_7th_grade: { en: 'Middle School Math — 7th', he: 'מתמטיקה — כיתה ז׳', icon: '7' },
  middle_school_math_8th_grade: { en: 'Middle School Math — 8th', he: 'מתמטיקה — כיתה ח׳', icon: '8' },
  middle_school_math_9th_grade: { en: 'Middle School Math — 9th', he: 'מתמטיקה — כיתה ט׳', icon: '9' },
  high_school_math_3_points: { en: 'High School Math — 3 pts', he: 'מתמטיקה — 3 יח״ל', icon: '3' },
  high_school_math_4_points: { en: 'High School Math — 4 pts', he: 'מתמטיקה — 4 יח״ל', icon: '4' },
  high_school_math_5_points: { en: 'High School Math — 5 pts', he: 'מתמטיקה — 5 יח״ל', icon: '5' },
  physics_high_school: { en: 'Physics — High School', he: 'פיזיקה — תיכון', icon: '⚛️' },
  physics_middle_school: { en: 'Physics — Middle School', he: 'פיזיקה — חטיבה', icon: '🔬' },
  physics_pre_university: { en: 'Physics Pre-University', he: 'פיזיקה לפני אוניברסיטה', icon: '⚡' },
  physics_1: { en: 'Physics 1', he: 'פיזיקה 1', icon: '⚛️' },
  physics_2: { en: 'Physics 2', he: 'פיזיקה 2', icon: '🔋' },
};

export function subjectLabel(slug: string, locale: 'en' | 'he' = 'en'): string {
  const entry = SUBJECT_LABELS[slug];
  if (!entry) return slug.replace(/_/g, ' ');
  return locale === 'he' ? entry.he : entry.en;
}

export function subjectIcon(slug: string): string {
  return SUBJECT_LABELS[slug]?.icon ?? '📚';
}
