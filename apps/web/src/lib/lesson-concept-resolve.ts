import { isAliasConceptId, resolveConceptAlias } from './concept-aliases';
import { isConceptInLessonIndex } from './lesson-index';

/**
 * Resolve which authored lesson to load for a catalog / URL concept id.
 * A dedicated lesson for `conceptId` always wins over syllabus alias redirects.
 */
export function resolveLessonConceptId(conceptId: string): string {
  if (isConceptInLessonIndex(conceptId)) return conceptId;
  return resolveConceptAlias(conceptId);
}

/** Alias-only syllabus slug that should redirect to its authored lesson target. */
export function aliasRedirectTarget(conceptId: string): string | null {
  if (!isAliasConceptId(conceptId)) return null;
  if (isConceptInLessonIndex(conceptId)) return null;
  const target = resolveConceptAlias(conceptId);
  if (target === conceptId) return null;
  if (!isConceptInLessonIndex(target)) return null;
  return target;
}

export { catalogDedupeKey } from './concept-aliases';
