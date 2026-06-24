import { seedLessons } from './seed-lessons';

export interface LessonSummary {
  id: string;
  title: string;
  est_minutes: number;
}

/** Maps seed `unit_id` values to curriculum category/section IDs. */
const UNIT_TO_SECTION: Record<string, { categoryId: string; sectionId: string }> = {
  'number-sense': { categoryId: 'math-middle', sectionId: 'numbers-and-operations' },
  fractions: { categoryId: 'math-middle', sectionId: 'fractions-and-decimals' },
  'decimals-and-percent': { categoryId: 'math-middle', sectionId: 'fractions-and-decimals' },
  'openstax-precalculus': { categoryId: 'pre-calculus', sectionId: 'functions-and-graphs' },
  'openstax-statistics': { categoryId: 'statistics', sectionId: 'descriptive-statistics' },
};

function sectionKey(categoryId: string, sectionId: string): string {
  return `${categoryId}/${sectionId}`;
}

const lessonsBySection = new Map<string, LessonSummary[]>();

for (const lesson of seedLessons) {
  const target = UNIT_TO_SECTION[lesson.unit_id];
  if (!target) continue;

  const key = sectionKey(target.categoryId, target.sectionId);
  const summary: LessonSummary = {
    id: lesson.id,
    title: lesson.title,
    est_minutes: lesson.est_minutes,
  };

  const existing = lessonsBySection.get(key) ?? [];
  existing.push(summary);
  lessonsBySection.set(key, existing);
}

export function getLessonsForSection(categoryId: string, sectionId: string): LessonSummary[] {
  return lessonsBySection.get(sectionKey(categoryId, sectionId)) ?? [];
}

export function getLessonCountForSection(categoryId: string, sectionId: string): number {
  return getLessonsForSection(categoryId, sectionId).length;
}
