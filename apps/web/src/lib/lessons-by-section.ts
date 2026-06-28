/**
 * Maps curriculum category sections to their available lesson summaries.
 *
 * Two sources are merged:
 *  1. The legacy seed-lessons snapshot (OpenStax foundations content)
 *  2. The AI-authored lesson index (`lessons-index.generated.json`) keyed by
 *     concept_id, which is also the lesson id stored in Neon.
 *
 * Section ↔ lesson mapping uses `CurriculumSection.concept_ids`: if a lesson's
 * id appears in `section.concept_ids`, that lesson belongs to the section.
 */
import { seedLessons } from './seed-lessons';
import { CURRICULUM_CATEGORIES } from './curriculum-categories';
import lessonsIndex from './lessons-index.generated.json';

export interface LessonSummary {
  id: string;
  title: string;
  title_he?: string;
  est_minutes: number;
}

interface LessonIndexEntry {
  id: string;
  title_en: string;
  title_he?: string;
  est_minutes: number;
  math_track: string[];
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

// ── Source 1: legacy seed lessons ──────────────────────────────────────────
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

// ── Source 2: AI-authored lessons keyed by concept_id ─────────────────────
const lessonIndexById = new Map<string, LessonIndexEntry>(
  (lessonsIndex as LessonIndexEntry[]).map((l) => [l.id, l]),
);

for (const category of CURRICULUM_CATEGORIES) {
  for (const section of category.sections) {
    const conceptIds = section.concept_ids ?? [];
    if (conceptIds.length === 0) continue;

    const key = sectionKey(category.id, section.id);
    const existing = lessonsBySection.get(key) ?? [];
    const existingIds = new Set(existing.map((l) => l.id));

    for (const conceptId of conceptIds) {
      if (existingIds.has(conceptId)) continue;
      const entry = lessonIndexById.get(conceptId);
      if (!entry) continue;

      existing.push({
        id: entry.id,
        title: entry.title_en,
        title_he: entry.title_he,
        est_minutes: entry.est_minutes,
      });
      existingIds.add(conceptId);
    }

    if (existing.length > 0) {
      lessonsBySection.set(key, existing);
    }
  }
}

export function getLessonsForSection(categoryId: string, sectionId: string): LessonSummary[] {
  return lessonsBySection.get(sectionKey(categoryId, sectionId)) ?? [];
}

export function getLessonCountForSection(categoryId: string, sectionId: string): number {
  return getLessonsForSection(categoryId, sectionId).length;
}
