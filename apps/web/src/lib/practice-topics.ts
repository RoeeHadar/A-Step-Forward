/**
 * Curated bilingual practice topics (ADR-0013 v2).
 * Full-catalog clusters → KG concept ids. Client-safe.
 */

export interface PracticeTopic {
  id: string;
  label_en: string;
  label_he: string;
  /** UI grouping (picker sections). */
  group_en: string;
  group_he: string;
  subject: 'math' | 'physics';
  concept_ids: readonly string[];
}

export const PRACTICE_TOPICS: readonly PracticeTopic[] = [
  // —— Math: school track ——
  {
    id: 'algebra',
    label_en: 'Algebra & equations',
    label_he: 'אלגברה ומשוואות',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'arithmetic',
      'algebra_basics',
      'equations_linear',
      'equations_quadratic',
      'inequalities',
      'fractions_algebraic',
      'exponents',
      'factoring',
      'word_problems',
    ],
  },
  {
    id: 'functions',
    label_en: 'Functions',
    label_he: 'פונקציות',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'functions_intro',
      'functions_linear',
      'functions_quadratic',
      'functions_exponential',
      'logarithms',
      'function_transformations',
      'function_analysis_extrema',
      'function_analysis_asymptotes',
    ],
  },
  {
    id: 'geometry',
    label_en: 'Plane geometry',
    label_he: 'הנדסת המישור',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'geometry_basics',
      'triangles_congruence',
      'quadrilaterals',
      'circles',
    ],
  },
  {
    id: 'analytic_geometry',
    label_en: 'Analytic geometry & vectors',
    label_he: 'הנדסה אנליטית ווקטורים',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'analytic_geometry_basic',
      'analytic_geometry',
      'vectors_2d',
      'vectors_plane',
    ],
  },
  {
    id: 'trigonometry',
    label_en: 'Trigonometry',
    label_he: 'טריגונומטריה',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'trigonometry_ratios',
      'trigonometry_identities',
      'trigonometry_equations',
      'trigonometry_plane_sine_cosine_law',
    ],
  },
  {
    id: 'sequences',
    label_en: 'Sequences & series',
    label_he: 'סדרות וטורים',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'sequences_arithmetic',
      'sequences_geometric',
      'sequences_limits',
      'uni_sequences_series',
    ],
  },
  {
    id: 'statistics_probability',
    label_en: 'Statistics & probability',
    label_he: 'סטטיסטיקה והסתברות',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'statistics_descriptive',
      'descriptive_stats',
      'descriptive_statistics',
      'probability_basic',
      'basic_probability',
      'combinatorics',
      'distributions',
      'normal_distribution_basics',
      'normal_distribution_z_scores',
      'probability_conditional_bayes',
      'linear_regression_correlation',
      'hypothesis_testing_intro',
    ],
  },
  {
    id: 'calculus_diff',
    label_en: 'Derivatives & limits',
    label_he: 'נגזרות וגבולות',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'limits',
      'limits_intro',
      'derivatives_intro',
      'derivatives_rules',
      'derivatives_applications',
      'derivatives_trigonometric',
      'derivatives_polynomial_rational',
      'derivatives_exponential_logarithm',
      'derivatives_chain_rule',
      'optimization_problems',
      'optimization_word_problems',
    ],
  },
  {
    id: 'calculus_int',
    label_en: 'Integrals',
    label_he: 'אינטגרלים',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'integrals_intro',
      'definite_integrals',
      'integrals_techniques',
      'integrals_applications',
      'integrals_trigonometric',
      'integrals_polynomial_rational',
      'integrals_substitution_basic',
      'integration_substitution',
      'areas_between_curves',
      'volumes_of_revolution_basic',
      'volumes_of_revolution',
    ],
  },
  {
    id: 'linear_algebra',
    label_en: 'Linear algebra',
    label_he: 'אלגברה לינארית',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'la_vectors',
      'la_matrices',
      'la_determinants',
      'la_vector_spaces',
      'la_eigenvalues',
      'la_orthogonality',
      'la_diagonalization',
    ],
  },
  {
    id: 'uni_calculus',
    label_en: 'University calculus',
    label_he: 'חשבון דיפרנציאלי ואינטגרלי (אוניברסיטה)',
    group_en: 'Math',
    group_he: 'מתמטיקה',
    subject: 'math',
    concept_ids: [
      'uni_functions_review',
      'uni_limits',
      'uni_derivatives',
      'uni_derivative_applications',
      'uni_integrals',
      'uni_integration_techniques',
      'uni_applications_integrals',
      'uni_multivariable',
      'uni_partial_derivatives',
      'uni_multiple_integrals',
      'uni_vector_fields',
      'uni_line_integrals',
    ],
  },
  // —— Physics ——
  {
    id: 'mechanics',
    label_en: 'Mechanics (kinematics & Newton)',
    label_he: 'מכניקה (קינמטיקה וניוטון)',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'units_measurement',
      'vectors_basics',
      'kinematics_1d',
      'kinematics_2d',
      'projectile_motion',
      'newton_laws',
      'newton_laws_general',
      'friction',
      'circular_motion',
      'circular_motion_gravitation',
      'gravitation',
    ],
  },
  {
    id: 'energy_momentum',
    label_en: 'Energy, work & momentum',
    label_he: 'אנרגיה, עבודה ותנע',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'work_energy',
      'work_energy_conservation',
      'work_energy_power',
      'conservation_energy',
      'momentum',
      'momentum_impulse_collisions',
      'collisions',
    ],
  },
  {
    id: 'rotation_oscillations',
    label_en: 'Rotation & oscillations',
    label_he: 'סיבוב ותנודות',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'torque',
      'static_equilibrium',
      'rotational_kinematics',
      'rotational_dynamics',
      'simple_harmonic_motion',
    ],
  },
  {
    id: 'waves_optics',
    label_en: 'Waves & optics',
    label_he: 'גלים ואופטיקה',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'waves_basics',
      'sound_waves',
      'doppler',
      'optics_geometric',
      'optics_physical',
      'geometric_optics',
      'geometric_optics_refraction',
      'em_waves',
    ],
  },
  {
    id: 'electricity',
    label_en: 'Electricity & circuits',
    label_he: 'חשמל ומעגלים',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'electrostatics',
      'coulomb_law',
      'electric_field',
      'electric_field_potential',
      'electric_potential',
      'electric_circuits',
      'dc_circuits_kirchhoff',
      'kirchhoff_laws',
      'capacitors_parallel_plate',
      'ac_circuits',
    ],
  },
  {
    id: 'magnetism',
    label_en: 'Magnetism & induction',
    label_he: 'מגנטיות והשראה',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'magnetism',
      'magnetic_force',
      'electromagnetic_induction',
      'faraday_induction',
    ],
  },
  {
    id: 'modern_physics',
    label_en: 'Modern physics',
    label_he: 'פיזיקה מודרנית',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'modern_physics_intro',
      'atomic_models',
      'nuclear_physics',
      'special_relativity',
      'photoelectric_effect',
    ],
  },
  {
    id: 'uni_physics',
    label_en: 'University physics track',
    label_he: 'פיזיקה אוניברסיטאית',
    group_en: 'Physics',
    group_he: 'פיזיקה',
    subject: 'physics',
    concept_ids: [
      'uni_vectors',
      'uni_kinematics',
      'uni_newtonian_mechanics',
      'uni_work_energy',
      'uni_momentum',
      'uni_rigid_body',
      'uni_oscillations',
      'uni_fluids',
      'uni_thermodynamics',
      'uni_electric_fields',
      'uni_potential',
      'uni_capacitance',
      'uni_dc_circuits',
      'uni_magnetic_fields',
      'uni_induction',
      'uni_ac_circuits',
      'uni_maxwell',
      'uni_em_waves',
      'uni_optics',
      'uni_quantum_intro',
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
  return [...new Set(ids)].slice(0, 12);
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

/** Topics grouped for the picker UI. */
export function practiceTopicsByGroup(
  lang: 'he' | 'en',
): Array<{ group: string; topics: readonly PracticeTopic[] }> {
  const order: string[] = [];
  const map = new Map<string, PracticeTopic[]>();
  for (const t of PRACTICE_TOPICS) {
    const g = lang === 'he' ? t.group_he : t.group_en;
    if (!map.has(g)) {
      map.set(g, []);
      order.push(g);
    }
    map.get(g)!.push(t);
  }
  return order.map((group) => ({ group, topics: map.get(group)! }));
}
