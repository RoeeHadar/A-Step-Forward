/**
 * Which course (/learn/[subject]) a concept lesson belongs under.
 *
 * Lesson pages render for any course slug, so the same lesson used to be
 * reachable under every course (~12 URLs per lesson). A concept belongs to a
 * course when the course's catalog lists it (directly, as a track variant
 * like `x__5pt`, or as an alias collapsing to the same catalog card). A
 * concept can legitimately sit in several courses (e.g. 4pt and 5pt); each of
 * those stays a real page because the course sets the level shown to
 * signed-out learners.
 */
import { CURRICULUM_CATEGORIES, getCategoryById, SUBJECT_TO_CATEGORY } from './curriculum-categories';
import type { CurriculumCategory } from './curriculum-categories';
import { catalogDedupeKey } from './lesson-concept-resolve';

const keysByCategory = new Map<string, Set<string>>();

function categoryKeys(category: CurriculumCategory): Set<string> {
  let keys = keysByCategory.get(category.id);
  if (!keys) {
    keys = new Set<string>();
    const ids = [...category.concept_ids, ...category.sections.flatMap((s) => s.concept_ids ?? [])];
    for (const id of ids) {
      keys.add(id);
      keys.add(catalogDedupeKey(id));
    }
    keysByCategory.set(category.id, keys);
  }
  return keys;
}

function categoryForSlug(subject: string): CurriculumCategory | undefined {
  return getCategoryById(SUBJECT_TO_CATEGORY[subject] ?? subject);
}

export function courseContainsConcept(subject: string, conceptId: string): boolean {
  const category = categoryForSlug(subject);
  if (!category) return false;
  const keys = categoryKeys(category);
  return keys.has(conceptId) || keys.has(catalogDedupeKey(conceptId));
}

/** Course ids that list this concept, in catalog order. */
export function coursesForConcept(conceptId: string): string[] {
  return CURRICULUM_CATEGORIES.filter((c) => courseContainsConcept(c.id, conceptId)).map((c) => c.id);
}

/**
 * The course slug a concept page should live under, or null when the current
 * URL is already right (or the concept isn't in any course catalog, e.g.
 * knowledge-graph-only concepts, which keep their URL).
 */
export function canonicalCourseRedirect(subject: string, conceptId: string): string | null {
  const current = categoryForSlug(subject);
  if (current && courseContainsConcept(current.id, conceptId)) {
    return current.id === subject ? null : current.id;
  }
  const first = coursesForConcept(conceptId)[0];
  return first && first !== subject ? first : null;
}
