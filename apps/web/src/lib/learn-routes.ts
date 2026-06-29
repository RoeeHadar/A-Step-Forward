import { CURRICULUM_CATEGORIES, getCategoryById, SUBJECT_TO_CATEGORY } from '@/lib/curriculum-categories';

/** Build a direct lesson URL for a concept page. */
export function learnConceptHref(subject: string, conceptId: string): string {
  return `/learn/${subject}/concept/${conceptId}`;
}

const KNOWN_UI_SLUGS = new Set([
  ...CURRICULUM_CATEGORIES.map((c) => c.id),
  ...Object.keys(SUBJECT_TO_CATEGORY),
  'high_school_math_3_points',
  'high_school_math_4_points',
  'high_school_math_5_points',
  'math',
  'physics',
]);

/**
 * Map a KG subject + learner profile to the UI subject slug used in `/learn/[subject]`.
 */
export function resolveLearnSubjectSlug(
  conceptId: string,
  kgSubject: string,
  pointsGroup?: string | null,
  subjects?: string[] | null,
): string {
  if (kgSubject === 'makhina') return 'makhina';

  if (KNOWN_UI_SLUGS.has(kgSubject)) {
    if (kgSubject === 'math') {
      if (pointsGroup === '3pt') return 'high_school_math_3pt';
      if (pointsGroup === '4pt') return 'high_school_math_4pt';
      if (pointsGroup === '5pt') return 'high_school_math_5pt';
    }
    return SUBJECT_TO_CATEGORY[kgSubject] ?? kgSubject;
  }

  const hsPhys = getCategoryById('hs_physics');
  if (
    hsPhys?.concept_ids.includes(conceptId) ||
    kgSubject === 'physics' ||
    subjects?.includes('physics')
  ) {
    return pointsGroup === 'hs_physics' ? 'hs_physics' : 'physics';
  }

  if (pointsGroup === '3pt') return 'high_school_math_3pt';
  if (pointsGroup === '4pt') return 'high_school_math_4pt';
  if (pointsGroup === '5pt') return 'high_school_math_5pt';

  return kgSubject || 'math';
}

export function learnConceptHrefFromProfile(
  conceptId: string,
  kgSubject: string,
  pointsGroup?: string | null,
  subjects?: string[] | null,
): string {
  const subject = resolveLearnSubjectSlug(conceptId, kgSubject, pointsGroup, subjects);
  return learnConceptHref(subject, conceptId);
}
