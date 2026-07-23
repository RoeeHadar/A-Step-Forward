/**
 * Curated bilingual practice topics (ADR-0013 v2).
 * Full-catalog clusters → KG concept ids. Client-safe.
 */

export interface PracticeTopic {
  id: string;
  label_en: string;
  label_he: string;
  subject: 'math' | 'physics';
  concept_ids: readonly string[];
}

export const PRACTICE_TOPICS: readonly PracticeTopic[] = [
  {
    id: 'functions',
    label_en: 'Functions',
    label_he: 'פונקציות',
    subject: 'math',
    concept_ids: [
      'functions_intro',
      'functions_linear',
      'functions_quadratic',
      'functions_exponential',
      'function_transformations',
    ],
  },
  {
    id: 'geometry',
    label_en: 'Geometry',
    label_he: 'הנדסה',
    subject: 'math',
    concept_ids: [
      'geometry_basics',
      'triangles_congruence',
      'circles',
      'analytic_geometry_basic',
      'analytic_geometry',
    ],
  },
  {
    id: 'algebra',
    label_en: 'Algebra',
    label_he: 'אלגברה',
    subject: 'math',
    concept_ids: [
      'algebra_basics',
      'equations_linear',
      'equations_quadratic',
      'inequalities',
      'factoring',
      'logarithms',
      'exponents',
    ],
  },
  {
    id: 'trigonometry',
    label_en: 'Trigonometry',
    label_he: 'טריגונומטריה',
    subject: 'math',
    concept_ids: [
      'trigonometry_ratios',
      'trigonometry_identities',
      'trigonometry_equations',
      'trigonometry_plane_sine_cosine_law',
    ],
  },
  {
    id: 'calculus_diff',
    label_en: 'Derivatives & limits',
    label_he: 'נגזרות וגבולות',
    subject: 'math',
    concept_ids: [
      'limits',
      'derivatives_intro',
      'derivatives_rules',
      'derivatives_applications',
      'derivatives_trigonometric',
    ],
  },
  {
    id: 'calculus_int',
    label_en: 'Integrals',
    label_he: 'אינטגרלים',
    subject: 'math',
    concept_ids: [
      'integrals_intro',
      'definite_integrals',
      'integrals_techniques',
      'integrals_applications',
      'integrals_trigonometric',
    ],
  },
  {
    id: 'mechanics',
    label_en: 'Mechanics',
    label_he: 'מכניקה',
    subject: 'physics',
    concept_ids: [
      'kinematics_1d',
      'kinematics_2d',
      'projectile_motion',
      'newton_laws',
      'work_energy',
      'momentum',
      'friction',
    ],
  },
] as const;

const byId = Object.fromEntries(PRACTICE_TOPICS.map((t) => [t.id, t]));

export function getPracticeTopic(id: string): PracticeTopic | undefined {
  return byId[id];
}

export function parsePracticeTopicIds(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  const ids = raw
    .filter((x): x is string => typeof x === 'string')
    .map((x) => x.trim())
    .filter((id) => Boolean(byId[id]));
  return [...new Set(ids)].slice(0, 8);
}

/** Union of concept ids for the selected topics. */
export function conceptIdsForTopics(topicIds: string[]): string[] {
  const out = new Set<string>();
  for (const id of topicIds) {
    const t = byId[id];
    if (!t) continue;
    for (const c of t.concept_ids) out.add(c);
  }
  return [...out];
}

export function practiceTopicLabels(
  topicIds: string[],
  lang: 'he' | 'en',
): string[] {
  return topicIds
    .map((id) => byId[id])
    .filter(Boolean)
    .map((t) => (lang === 'he' ? t!.label_he : t!.label_en));
}
