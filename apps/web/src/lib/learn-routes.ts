import { CURRICULUM_CATEGORIES, type PointsLevel } from '@/lib/curriculum-categories';

/** Build a direct lesson URL for a concept page. */
export function learnConceptHref(subject: string, conceptId: string): string {
  return `/learn/${subject}/concept/${conceptId}`;
}

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

  const knownUiSlugs = new Set([
    'high_school_math_3_points',
    'high_school_math_4_points',
    'high_school_math_5_points',
    'hs_physics',
    'physics',
    'biology',
    'makhina',
    'math',
  ]);
  if (knownUiSlugs.has(kgSubject)) {
    if (kgSubject === 'math') {
      if (pointsGroup === '3pt') return 'high_school_math_3_points';
      if (pointsGroup === '4pt') return 'high_school_math_4_points';
      if (pointsGroup === '5pt') return 'high_school_math_5_points';
    }
    return kgSubject;
  }

  const bioCat = CURRICULUM_CATEGORIES.find((c) => c.id === 'biology-4pt');
  if (
    bioCat?.concept_ids.includes(conceptId) ||
    kgSubject === 'biology' ||
    subjects?.includes('biology')
  ) {
    return 'biology';
  }

  const physCat = CURRICULUM_CATEGORIES.find((c) => c.id === 'physics-hs');
  if (
    physCat?.concept_ids.includes(conceptId) ||
    kgSubject === 'physics' ||
    subjects?.includes('physics')
  ) {
    return pointsGroup === 'hs_physics' ? 'hs_physics' : 'physics';
  }

  if (pointsGroup === '3pt') return 'high_school_math_3_points';
  if (pointsGroup === '4pt') return 'high_school_math_4_points';
  if (pointsGroup === '5pt') return 'high_school_math_5_points';

  return kgSubject || 'math';
}

export function learnConceptHrefFromProfile(
  conceptId: string,
  kgSubject: string,
  pointsGroup?: string | null,
  subjects?: string[] | null,
): string {
  const subject = resolveLearnSubjectSlug(
    conceptId,
    kgSubject,
    pointsGroup as PointsLevel | null,
    subjects,
  );
  return learnConceptHref(subject, conceptId);
}
