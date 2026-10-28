/**
 * "Is there an authored lesson for this concept?" without loading the lesson
 * payloads. Safe to import from client components.
 *
 * lessons-bundle.generated.json is ~29 MB; importing it from anything a
 * 'use client' module can reach ships it to the browser (M6). The generator
 * (scripts/generate-lessons-artifacts.mjs) writes the lesson index and the
 * bundle from the same loop, so they hold the same concept ids; this module
 * answers from the ~127 KB index instead. lesson-bundle-membership.test.ts
 * asserts both the id parity and the same answers as the old bundle lookup.
 */
import { CONCEPT_ID_ALIASES, resolveConceptAlias } from './concept-aliases';
import { isConceptInLessonIndex } from './lesson-index';

export function isConceptInBundle(conceptId: string): boolean {
  if (isConceptInLessonIndex(conceptId)) return true;
  if (isConceptInLessonIndex(resolveConceptAlias(conceptId))) return true;
  const mapped = Object.hasOwn(CONCEPT_ID_ALIASES, conceptId)
    ? CONCEPT_ID_ALIASES[conceptId]
    : undefined;
  return mapped != null && isConceptInLessonIndex(mapped);
}
