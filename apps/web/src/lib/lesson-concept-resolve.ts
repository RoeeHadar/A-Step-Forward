import {
  isAliasConceptId,
  resolveConceptAlias,
  catalogDedupeKey as aliasCatalogDedupeKey,
} from './concept-aliases';
import { isConceptInLessonIndex } from './lesson-index';

/** Track suffixes used for per-track variant lesson ids (`<canonical>__<track>`). */
export const VARIANT_TRACKS = ['3pt', '4pt', '5pt', 'uni'] as const;
export type VariantTrack = (typeof VARIANT_TRACKS)[number];

const VARIANT_SUFFIX_RE = /__(?:3pt|4pt|5pt|uni)$/;

/** Strip a `__3pt|__4pt|__5pt|__uni` suffix to the catalog/KG canonical id. */
export function stripVariantSuffix(conceptId: string): string {
  return String(conceptId || '').replace(VARIANT_SUFFIX_RE, '');
}

/** True when this id is a track-owned variant file, not the canonical lesson. */
export function isTrackVariantLessonId(conceptId: string): boolean {
  return VARIANT_SUFFIX_RE.test(String(conceptId || ''));
}

/**
 * Resolve which authored lesson to load for a catalog / URL concept id.
 * A dedicated lesson for `conceptId` always wins over syllabus alias redirects.
 */
export function resolveLessonConceptId(conceptId: string): string {
  if (isTrackVariantLessonId(conceptId) && isConceptInLessonIndex(conceptId)) {
    return conceptId;
  }
  const stripped = stripVariantSuffix(conceptId);
  if (isConceptInLessonIndex(stripped)) return stripped;
  if (isConceptInLessonIndex(conceptId)) return conceptId;
  return resolveConceptAlias(stripped);
}

function trackForLevel(level: string | null | undefined): VariantTrack | null {
  if (!level) return null;
  const norm = String(level).trim().toLowerCase();
  if ((VARIANT_TRACKS as readonly string[]).includes(norm)) return norm as VariantTrack;
  if (
    norm === 'university' ||
    norm === 'calc1' ||
    norm === 'calc2' ||
    norm === 'analysis' ||
    norm === 'la' ||
    norm === 'university_prep'
  ) {
    return 'uni';
  }
  return null;
}

/**
 * Pick the most level-appropriate authored lesson id for a catalog / URL concept.
 * Per-track variants use the id form `<canonical>__<track>` (file / bundle key).
 */
export function resolveVariantLessonId(
  conceptId: string,
  learnerLevel?: string | null,
): string {
  const stripped = stripVariantSuffix(conceptId);
  const canonical = isConceptInLessonIndex(stripped)
    ? stripped
    : resolveLessonConceptId(stripped);
  const track = trackForLevel(learnerLevel);
  if (track) {
    const variant = `${canonical}__${track}`;
    if (isConceptInLessonIndex(variant)) return variant;
  }
  if (isConceptInLessonIndex(canonical)) return canonical;
  return resolveLessonConceptId(stripped);
}

/** Sibling track-variants that exist for a concept (for "advanced version" links). */
export function variantLessonIds(
  conceptId: string,
): { track: VariantTrack; lessonId: string }[] {
  const stripped = stripVariantSuffix(conceptId);
  const canonical = isConceptInLessonIndex(stripped)
    ? stripped
    : resolveLessonConceptId(stripped);
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

/**
 * Catalog grids: one card per canonical topic — collapse `__4pt`/`__5pt`/`__uni`.
 */
export function catalogDedupeKey(conceptId: string): string {
  const stripped = stripVariantSuffix(conceptId);
  if (isTrackVariantLessonId(conceptId)) return stripped;
  return aliasCatalogDedupeKey(stripped);
}
