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

/** Track suffixes used for per-track variant lesson ids (`<canonical>__<track>`). */
export const VARIANT_TRACKS = ['3pt', '4pt', '5pt'] as const;
export type VariantTrack = (typeof VARIANT_TRACKS)[number];

function trackForLevel(level: string | null | undefined): VariantTrack | null {
  if (!level) return null;
  const norm = String(level).trim().toLowerCase();
  return (VARIANT_TRACKS as readonly string[]).includes(norm) ? (norm as VariantTrack) : null;
}

/**
 * Pick the most level-appropriate authored lesson id for a catalog / URL concept.
 * Per-track variants use the id form `<canonical>__<track>` and carry
 * `concept_id = <canonical>` for KG / mastery. When the learner's track has a
 * dedicated variant, it wins; otherwise fall back to the canonical, level-agnostic
 * lesson. This is a pure lookup so it is safe in both server and client bundles.
 */
export function resolveVariantLessonId(
  conceptId: string,
  learnerLevel?: string | null,
): string {
  const canonical = resolveLessonConceptId(conceptId);
  const track = trackForLevel(learnerLevel);
  if (track) {
    const variant = `${canonical}__${track}`;
    if (isConceptInLessonIndex(variant)) return variant;
  }
  return canonical;
}

/** Sibling track-variants that exist for a concept (for "advanced version" links). */
export function variantLessonIds(
  conceptId: string,
): { track: VariantTrack; lessonId: string }[] {
  const canonical = resolveLessonConceptId(conceptId);
  const out: { track: VariantTrack; lessonId: string }[] = [];
  for (const track of VARIANT_TRACKS) {
    const variant = `${canonical}__${track}`;
    if (isConceptInLessonIndex(variant)) out.push({ track, lessonId: variant });
  }
  return out;
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
