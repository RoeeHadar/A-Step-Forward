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
/** Underscore track-named lessons: `limits_4pt`, `analytic_geometry_5pt`, `combinatorics_5pt`. */
const UNDERSCORE_TRACK_RE = /_(3pt|4pt|5pt|uni)$/;

/**
 * Canonical syllabus id → preferred authored lesson id per learner track.
 * Covers track-named files that do not use the `__track` suffix convention.
 */
export const TRACK_NAMED_LESSONS: Record<string, Partial<Record<VariantTrack, string>>> = {
  limits: { '4pt': 'limits_4pt', '5pt': 'limits_5pt', uni: 'limits_epsilon_delta' },
  combinatorics: { '5pt': 'combinatorics__5pt' },
  sequences_arithmetic: { '5pt': 'sequences_5pt' },
  sequences_geometric: { '5pt': 'sequences_5pt' },
  logarithms: { '5pt': 'logarithms__5pt' },
  function_analysis_4pt: { '4pt': 'function_analysis_4pt', '5pt': 'function_analysis_5pt' },
  function_analysis_5pt: { '5pt': 'function_analysis_5pt' },
  plane_trigonometry_right_triangle: {
    '5pt': 'plane_trigonometry_right_triangle__5pt',
  },
  euclidean_geometry_circles: { '5pt': 'euclidean_geometry_circles__5pt' },
  riemann_integral_ftc: { '5pt': 'riemann_integral_ftc__5pt', uni: 'riemann_integral_ftc' },
  implicit_differentiation: {
    '5pt': 'implicit_differentiation',
    uni: 'implicit_differentiation__uni',
  },
  analytic_geometry: {
    '4pt': 'analytic_geometry_4pt',
    '5pt': 'analytic_geometry__5pt',
  },
};

/** Strip a `__3pt|__4pt|__5pt|__uni` or `_3pt|_4pt|_5pt|_uni` suffix to the catalog id. */
export function stripVariantSuffix(conceptId: string): string {
  const raw = String(conceptId || '');
  if (VARIANT_SUFFIX_RE.test(raw)) return raw.replace(VARIANT_SUFFIX_RE, '');
  // Only strip underscore track suffixes for known track-named families
  const m = raw.match(UNDERSCORE_TRACK_RE);
  if (!m) return raw;
  const base = raw.replace(UNDERSCORE_TRACK_RE, '');
  if (base in TRACK_NAMED_LESSONS || Object.values(TRACK_NAMED_LESSONS).some((m) => Object.values(m).includes(raw))) {
    return base;
  }
  // analytic_geometry_4pt → analytic_geometry; combinatorics_5pt → combinatorics
  if (
    base === 'analytic_geometry' ||
    base === 'limits' ||
    base === 'combinatorics' ||
    base === 'sequences' ||
    base === 'function_analysis'
  ) {
    return base === 'sequences' ? 'sequences_arithmetic' : base;
  }
  return raw;
}

/** True when this id is a track-owned variant file, not the canonical lesson. */
export function isTrackVariantLessonId(conceptId: string): boolean {
  const id = String(conceptId || '');
  if (VARIANT_SUFFIX_RE.test(id)) return true;
  if (!UNDERSCORE_TRACK_RE.test(id)) return false;
  const stripped = stripVariantSuffix(id);
  return stripped !== id;
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

function pickTrackNamed(canonical: string, track: VariantTrack): string | null {
  const mapped = TRACK_NAMED_LESSONS[canonical]?.[track];
  if (mapped && isConceptInLessonIndex(mapped)) return mapped;
  // Generic underscore form: limits_4pt, analytic_geometry_5pt
  const underscored = `${canonical}_${track === 'uni' ? 'uni' : track}`;
  if (isConceptInLessonIndex(underscored)) return underscored;
  return null;
}

/**
 * Pick the most level-appropriate authored lesson id for a catalog / URL concept.
 * Tries `__track` variants, then track-named aliases (`limits_4pt`), then canonical.
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
    const dunder = `${canonical}__${track}`;
    if (isConceptInLessonIndex(dunder)) return dunder;
    const named = pickTrackNamed(canonical, track);
    if (named) return named;
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
  const seen = new Set<string>();
  for (const track of VARIANT_TRACKS) {
    const dunder = `${canonical}__${track}`;
    const named = pickTrackNamed(canonical, track);
    const lessonId = isConceptInLessonIndex(dunder) ? dunder : named;
    if (!lessonId || seen.has(lessonId)) continue;
    seen.add(lessonId);
    out.push({ track, lessonId });
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
