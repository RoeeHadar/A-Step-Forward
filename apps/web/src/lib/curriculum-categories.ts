/**
 * Curriculum category catalogue — aligned with Israeli Bagrut syllabuses and
 * standard university courses (Technion / Hebrew University / Tel Aviv University).
 *
 * Sources:
 *   - Misrad HaChinuch questionnaire specs + past Bagrut papers 2019-2024
 *   - Technion & HUJI course syllabuses for Calc 1/2, Physics 1/2, LA, Stats
 *   - Bagrut math 3pt (172/371/372), 4pt (471/472), 5pt (571/572)
 *   - Bagrut physics (036-361 mechanics, 036-371 electricity, radiation & matter)
 *
 * Each category carries:
 *   - `id`                   – stable identifier (used in URLs + DB queries)
 *   - `heLabel` / `enLabel`  – bilingual display names
 *   - `emoji`                – UI icon
 *   - `points_levels`        – learner profile tags
 *   - `bagrut_questionnaires`– official questionnaire numbers (Bagrut subjects only)
 *   - `sections`             – ordered chapters, each with concept_ids slice
 *   - `concept_ids`          – union of all concept IDs in scope for this subject
 */

export type PointsLevel =
  | '3pt'
  | '4pt'
  | '5pt'
  | 'hs_physics'
  | 'calc1'
  | 'calculus_2'
  | 'la'
  | 'university_physics_1'
  | 'university_physics_2'
  | 'stats_prob'
  | 'makhina';

export interface CurriculumSection {
  id: string;
  heLabel: string;
  enLabel: string;
  /** KG concept IDs that belong to this section */
  concept_ids?: string[];
}

export interface CurriculumCategory {
  id: string;
  heLabel: string;
  enLabel: string;
  emoji: string;
  points_levels: PointsLevel[];
  /** Official Bagrut questionnaire numbers (empty for non-Bagrut tracks) */
  bagrut_questionnaires?: string[];
  sections: CurriculumSection[];
  /** Ordered list of all KG concept IDs in scope for this category */
  concept_ids: string[];
}

// ─────────────────────────────────────────────────────────────────────────────
// MATH — 3 UNITS  (Bagrut 172 / 371 / 372)
// NO calculus, NO vectors, NO complex numbers
// ─────────────────────────────────────────────────────────────────────────────
const MATH_3PT_NEW_CONCEPTS = [
  'descriptive_statistics',
  'basic_probability',
  'normal_distribution_basics',
  'statistics_descriptive',
  'basic_statistics_3pt',
  'probability_basics_3pt',
  'probability_conditional_3pt',
  'geometry_basics',
  'circles',
  'triangles_congruence',
  'equations_linear',
  'functions_linear',
  'functions_quadratic',
  'functions_exponential',
  'trigonometry_ratios',
  'percentages_and_interest',
];

// Keep old KG concept IDs so that conceptIdsForLevel('3pt') still covers the knowledge graph.
const MATH_3PT_KG_LEGACY = [
  'arithmetic',
  'algebra_basics',
  'equations_linear',
  'equations_quadratic',
  'inequalities',
  'exponents',
  'factoring',
  'fractions_algebraic',
  'word_problems',
  'functions_intro',
  'functions_linear',
  'functions_quadratic',
  'functions_exponential',
  'sequences_arithmetic',
  'sequences_geometric',
  'analytic_geometry_basic',
  'geometry_basics',
  'trigonometry_ratios',
  'statistics_descriptive',
  'descriptive_stats',
  'probability_basic',
];
const MATH_3PT_CONCEPTS = [...new Set([...MATH_3PT_NEW_CONCEPTS, ...MATH_3PT_KG_LEGACY])];

// ─────────────────────────────────────────────────────────────────────────────
// MATH — 4 UNITS  (Bagrut 471 / 472)
// ─────────────────────────────────────────────────────────────────────────────
const MATH_4PT_NEW_CONCEPTS = [
  'derivatives_intro',
  'derivatives_polynomial_rational',
  'derivatives_rules',
  'derivatives_applications',
  'derivatives_chain_rule',
  'function_analysis_extrema',
  'optimization_word_problems',
  'integrals_intro',
  'integrals_polynomial_rational',
  'areas_between_curves',
  'volumes_of_revolution_basic',
  'derivatives_exponential_logarithm',
  'logarithmic_equations',
  'analytic_geometry',
  'analytic_geometry_lines_circles',
  'trigonometry_plane_sine_cosine_law',
  'descriptive_statistics',
  'normal_distribution_z_scores',
  'linear_regression_correlation',
  'hypothesis_testing_intro',
  'sequences_arithmetic',
  'sequences_geometric',
  'vectors_plane',
  'vectors_2d',
];
const MATH_4PT_KG_LEGACY = [
  'quadrilaterals',
  'triangles_congruence',
  'circles',
  'combinatorics',
  'analytic_geometry',
  'logarithms',
];
const MATH_4PT_CONCEPTS = [...new Set([...MATH_4PT_NEW_CONCEPTS, ...MATH_4PT_KG_LEGACY])];

// ─────────────────────────────────────────────────────────────────────────────
// MATH — 5 UNITS  (Bagrut 571 / 572)
// HAS: induction, complex numbers, full trig calculus, Bernoulli, conics, 3D vectors
// ─────────────────────────────────────────────────────────────────────────────
const MATH_5PT_NEW_CONCEPTS = [
  'derivatives_intro',
  'derivatives_chain_rule',
  'derivatives_trigonometric',
  'function_analysis_asymptotes',
  'integrals_trigonometric',
  'integrals_substitution_basic',
  'volumes_of_revolution',
  'derivatives_exponential_logarithm',
  'sequences_arithmetic',
  'sequences_geometric',
  'mathematical_induction',
  'distributions',
  'trigonometry_identities',
  'trigonometry_equations',
  'analytic_geometry',
  'analytic_geometry_conics',
  'circles',
  'vectors_dot_product_3d',
  'complex_numbers_de_moivre',
  'probability_conditional_bayes',
];
const MATH_5PT_KG_LEGACY = [
  'logarithms',
  'function_transformations',
  'trigonometry_identities',
  'trigonometry_equations',
  'analytic_geometry',
  'vectors_2d',
  'distributions',
  'limits',
  'continuity',
  'derivatives_intro',
  'derivatives_rules',
  'derivatives_applications',
  'optimization_problems',
  'integrals_intro',
  'definite_integrals',
  'integrals_techniques',
  'integrals_applications',
  'complex_numbers',
];
const MATH_5PT_CONCEPTS = [...new Set([...MATH_5PT_NEW_CONCEPTS, ...MATH_5PT_KG_LEGACY])];

// ─────────────────────────────────────────────────────────────────────────────
// PHYSICS — Bagrut 5 units
// ─────────────────────────────────────────────────────────────────────────────
const HS_PHYSICS_CONCEPTS = [
  'kinematics_1d',
  'projectile_motion',
  'newton_laws',
  'work_energy_conservation',
  'momentum',
  'circular_motion_gravitation',
  'coulomb_law',
  'electric_field_potential',
  'kirchhoff_laws',
  'capacitors_parallel_plate',
  'magnetic_force',
  'faraday_induction',
  'geometric_optics_refraction',
  'em_waves',
  'photoelectric_effect',
  'units_measurement',
  'vectors_basics',
  'kinematics_2d',
  'friction',
  'circular_motion',
  'gravitation',
  'work_energy',
  'conservation_energy',
  'collisions',
  'simple_harmonic_motion',
  'torque',
  'static_equilibrium',
  'rotational_kinematics',
  'rotational_dynamics',
  'waves_basics',
  'sound_waves',
  'doppler',
  'optics_geometric',
  'optics_physical',
  'electrostatics',
  'electric_field',
  'electric_circuits',
  'magnetism',
  'electromagnetic_induction',
  'ac_circuits',
  'modern_physics_intro',
  'atomic_models',
  'nuclear_physics',
  'special_relativity',
  'angular_momentum',
];

// ─────────────────────────────────────────────────────────────────────────────
// UNIVERSITY PHYSICS 1 — Calculus-based mechanics (Technion / HUJI)
// ─────────────────────────────────────────────────────────────────────────────
const UNI_PHYSICS_1_CONCEPTS = [
  'kinematics_2d',
  'vectors_2d',
  'newton_laws',
  'rigid_body_torque_equilibrium',
  'work_energy',
  'momentum',
  'angular_momentum_particles',
  'center_of_mass_uni',
  'harmonic_oscillation',
  'fluids_hydrostatics',
];

// ─────────────────────────────────────────────────────────────────────────────
// UNIVERSITY PHYSICS 2 — Calculus-based E&M (Technion / HUJI)
// ─────────────────────────────────────────────────────────────────────────────
const UNI_PHYSICS_2_CONCEPTS = [
  'electrostatics',
  'electric_field_gauss',
  'electric_field',
  'kirchhoff_laws',
  'magnetic_field_biot_savart',
  'ampere_law',
  'faraday_induction_uni',
  'maxwell_equations',
  'optics_geometric',
  'optics_physical',
];

// ─────────────────────────────────────────────────────────────────────────────
// מכינה — university prep bridge (Bagrut 5pt math + physics, reinforced)
// ─────────────────────────────────────────────────────────────────────────────
const MAKHINA_CONCEPTS = [
  'limits_intro',
  'limits_epsilon_delta',
  'derivatives_intro',
  'derivatives_chain_rule',
  'derivatives_trigonometric',
  'integrals_intro',
  'integrals_substitution_basic',
  'volumes_of_revolution',
  'derivatives_exponential_logarithm',
  'la_vectors',
  'la_matrices',
  'la_diagonalization',
  'la_orthogonality',
  'la_determinants',
  'la_vector_spaces',
  'eigenvalues_eigenvectors',
  'statistics_descriptive',
  'probability_basic',
  'statistics_inference',
  'normal_distribution_z_scores',
  'algebra_basics',
  'word_problems',
  'sequences_arithmetic',
  'sequences_geometric',
  'analytic_geometry',
  'trigonometry_identities',
  'fractions_and_ratios',
  'linear_equations_basics',
  'percentages_and_interest',
  'geometry_area_perimeter',
];

// ─────────────────────────────────────────────────────────────────────────────
// CALCULUS 1 — University (real numbers → derivatives + function analysis, NO integrals)
// Technion: sequences, ε-δ, derivatives, MVT, Taylor, L'Hôpital, function analysis
// ─────────────────────────────────────────────────────────────────────────────
const CALCULUS_1_CONCEPTS = [
  'limits_intro',
  'continuity',
  'limits_epsilon_delta',
  'derivatives_intro',
  'derivatives_chain_rule',
  'derivatives_applications',
  'mean_value_theorem',
  'sequences_limits',
  'taylor_formula',
  'function_analysis_asymptotes',
  'optimization_problems',
  'derivatives_rules',
  'limits',
];

// ─────────────────────────────────────────────────────────────────────────────
// CALCULUS 2 — University (integrals + series + multivariable)
// ─────────────────────────────────────────────────────────────────────────────
const CALCULUS_2_CONCEPTS = [
  'integrals_intro',
  'integration_substitution',
  'integration_by_parts',
  'definite_integrals',
  'taylor_formula',
  'limits',
  'partial_derivatives',
  'double_integrals',
  'integrals_techniques',
  'integrals_applications',
];

// ─────────────────────────────────────────────────────────────────────────────
// LINEAR ALGEBRA — University
// ─────────────────────────────────────────────────────────────────────────────
const LINEAR_ALGEBRA_CONCEPTS = [
  'la_matrices',
  'la_determinants',
  'la_vectors',
  'la_vector_spaces',
  'la_diagonalization',
  'la_orthogonality',
  'eigenvalues_eigenvectors',
  'la_eigenvalues',
];

// ─────────────────────────────────────────────────────────────────────────────
// STATISTICS & PROBABILITY — University
// ─────────────────────────────────────────────────────────────────────────────
const STATS_PROB_CONCEPTS = [
  'probability_basic',
  'probability_conditional_bayes',
  'distributions',
  'normal_distribution_z_scores',
  'statistics_inference',
  'central_limit_theorem',
  'hypothesis_testing_intro',
  'hypothesis_testing',
  'hypothesis_testing_z_t',
  'linear_regression_correlation',
  'linear_regression_least_squares',
  'correlation_coefficient',
  'confidence_intervals',
  'chi_square_goodness_of_fit',
  'anova_one_way',
  'chi_square_tests',
  'statistics_descriptive',
  'descriptive_stats',
  'combinatorics',
];

// ─────────────────────────────────────────────────────────────────────────────
export const CURRICULUM_CATEGORIES: CurriculumCategory[] = [
  // ──────────────────────────────────────────────────────────────────────────
  // MATH 3pt
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'high_school_math_3pt',
    heLabel: 'מתמטיקה לבגרות — 3 יחידות',
    enLabel: 'Bagrut Math — 3 Units',
    emoji: '🔢',
    points_levels: ['3pt'],
    bagrut_questionnaires: ['172', '371', '372'],
    concept_ids: MATH_3PT_CONCEPTS,
    sections: [
      {
        id: 'statistics_probability_3pt',
        heLabel: 'סטטיסטיקה והסתברות',
        enLabel: 'Statistics & Probability',
        concept_ids: [
          'descriptive_statistics',
          'basic_probability',
          'normal_distribution_basics',
          'statistics_descriptive',
          'basic_statistics_3pt',
          'probability_basics_3pt',
          'probability_conditional_3pt',
          'descriptive_stats',
          'probability_basic',
        ],
      },
      {
        id: 'geometry_3pt',
        heLabel: 'גאומטריה ומדידה',
        enLabel: 'Geometry & Measurement',
        concept_ids: [
          'geometry_basics',
          'circles',
          'triangles_congruence',
          'analytic_geometry_basic',
        ],
      },
      {
        id: 'functions_3pt',
        heLabel: 'פונקציות ואלגברה',
        enLabel: 'Functions & Algebra',
        concept_ids: [
          'equations_linear',
          'functions_linear',
          'functions_quadratic',
          'functions_exponential',
          'algebra_basics',
          'arithmetic',
          'equations_quadratic',
          'exponents',
          'factoring',
          'fractions_algebraic',
          'inequalities',
          'word_problems',
          'functions_intro',
          'sequences_arithmetic',
          'sequences_geometric',
        ],
      },
      {
        id: 'trigonometry_3pt',
        heLabel: 'טריגונומטריה בסיסית',
        enLabel: 'Basic Trigonometry',
        concept_ids: [ 'trigonometry_ratios' ],
      },
      {
        id: 'applied_3pt',
        heLabel: 'מתמטיקה יישומית',
        enLabel: 'Applied Math',
        concept_ids: [ 'percentages_and_interest' ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // MATH 4pt
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'high_school_math_4pt',
    heLabel: 'מתמטיקה לבגרות — 4 יחידות',
    enLabel: 'Bagrut Math — 4 Units',
    emoji: '📏',
    points_levels: ['4pt'],
    bagrut_questionnaires: ['471', '472'],
    concept_ids: MATH_4PT_CONCEPTS,
    sections: [
      {
        id: 'bridging_4pt',
        heLabel: 'גשר מ-3 ל-4 יחידות',
        enLabel: 'Bridging from 3pt',
        concept_ids: [
          'algebra_basics',
          'equations_linear',
          'equations_quadratic',
          'word_problems',
          'factoring',
          'analytic_geometry_basic',
          'sequences_arithmetic',
          'sequences_geometric',
        ],
      },
      {
        id: 'calculus_4pt',
        heLabel: 'חשבון דיפרנציאלי ואינטגרלי',
        enLabel: 'Calculus',
        concept_ids: [
          'derivatives_intro',
          'derivatives_polynomial_rational',
          'derivatives_rules',
          'derivatives_applications',
          'derivatives_chain_rule',
          'function_analysis_extrema',
          'optimization_word_problems',
          'integrals_intro',
          'integrals_polynomial_rational',
          'areas_between_curves',
          'volumes_of_revolution_basic',
          'derivatives_exponential_logarithm',
          'logarithmic_equations',
          'logarithms',
        ],
      },
      {
        id: 'analytic_geometry_4pt',
        heLabel: 'גאומטריה אנליטית',
        enLabel: 'Analytic Geometry',
        concept_ids: [
          'analytic_geometry',
          'analytic_geometry_lines_circles',
          'trigonometry_plane_sine_cosine_law',
          'circles',
          'quadrilaterals',
          'triangles_congruence',
        ],
      },
      {
        id: 'statistics_4pt',
        heLabel: 'סטטיסטיקה והסתברות',
        enLabel: 'Statistics & Probability',
        concept_ids: [
          'descriptive_statistics',
          'normal_distribution_z_scores',
          'linear_regression_correlation',
          'hypothesis_testing_intro',
          'combinatorics',
        ],
      },
      {
        id: 'sequences_4pt',
        heLabel: 'סדרות',
        enLabel: 'Sequences',
        concept_ids: [ 'sequences_arithmetic',
          'sequences_geometric' ],
      },
      {
        id: 'vectors_4pt',
        heLabel: 'וקטורים',
        enLabel: 'Vectors',
        concept_ids: [ 'vectors_plane',
          'vectors_2d' ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // MATH 5pt
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'high_school_math_5pt',
    heLabel: 'מתמטיקה לבגרות — 5 יחידות',
    enLabel: 'Bagrut Math — 5 Units',
    emoji: '🔢',
    points_levels: ['5pt'],
    bagrut_questionnaires: ['571', '572'],
    concept_ids: MATH_5PT_CONCEPTS,
    sections: [
      {
        id: 'calculus_5pt',
        heLabel: 'חשבון דיפרנציאלי ואינטגרלי',
        enLabel: 'Calculus',
        concept_ids: [
          'derivatives_intro',
          'derivatives_chain_rule',
          'derivatives_trigonometric',
          'function_analysis_asymptotes',
          'integrals_trigonometric',
          'integrals_substitution_basic',
          'volumes_of_revolution',
          'derivatives_exponential_logarithm',
          'limits',
          'continuity',
          'derivatives_rules',
          'derivatives_applications',
          'integrals_intro',
          'definite_integrals',
          'integrals_techniques',
          'integrals_applications',
          'optimization_problems',
        ],
      },
      {
        id: 'algebra_sequences_5pt',
        heLabel: 'אלגברה וסדרות',
        enLabel: 'Algebra & Sequences',
        concept_ids: [
          'sequences_arithmetic',
          'sequences_geometric',
          'mathematical_induction',
          'distributions',
          'function_transformations',
          'logarithms',
        ],
      },
      {
        id: 'trigonometry_5pt',
        heLabel: 'טריגונומטריה',
        enLabel: 'Trigonometry',
        concept_ids: [
          'trigonometry_identities',
          'trigonometry_equations',
        ],
      },
      {
        id: 'geometry_5pt',
        heLabel: 'גאומטריה אנליטית',
        enLabel: 'Analytic Geometry',
        concept_ids: [ 'analytic_geometry',
          'analytic_geometry_conics',
          'circles' ],
      },
      {
        id: 'vectors_complex_5pt',
        heLabel: 'וקטורים ומספרים מרוכבים',
        enLabel: 'Vectors & Complex Numbers',
        concept_ids: [ 'vectors_dot_product_3d',
          'complex_numbers_de_moivre',
          'vectors_2d',
          'complex_numbers' ],
      },
      {
        id: 'probability_5pt',
        heLabel: 'הסתברות',
        enLabel: 'Probability & Combinatorics',
        concept_ids: [ 'probability_conditional_bayes',
          'distributions' ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // PHYSICS — Bagrut 5 units (HS)
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'hs_physics',
    heLabel: 'פיזיקה לבגרות — 5 יחידות',
    enLabel: 'Bagrut Physics — 5 Units',
    emoji: '⚡',
    points_levels: ['hs_physics'],
    bagrut_questionnaires: ['036-361 (מכניקה)', '036-371 (חשמל)', 'קרינה וחומר', 'מעבדה'],
    concept_ids: HS_PHYSICS_CONCEPTS,
    sections: [
      {
        id: 'mechanics_hs',
        heLabel: 'מכניקה',
        enLabel: 'Mechanics',
        concept_ids: [
          'kinematics_1d',
          'projectile_motion',
          'newton_laws',
          'work_energy_conservation',
          'momentum',
          'circular_motion_gravitation',
          'units_measurement',
          'vectors_basics',
          'kinematics_2d',
          'friction',
          'circular_motion',
          'gravitation',
          'work_energy',
          'conservation_energy',
          'collisions',
          'simple_harmonic_motion',
          'torque',
          'static_equilibrium',
          'rotational_kinematics',
          'rotational_dynamics',
          'angular_momentum',
        ],
      },
      {
        id: 'electricity_hs',
        heLabel: 'חשמל ומגנטיות',
        enLabel: 'Electricity & Magnetism',
        concept_ids: [
          'coulomb_law',
          'electric_field_potential',
          'kirchhoff_laws',
          'capacitors_parallel_plate',
          'magnetic_force',
          'faraday_induction',
          'electrostatics',
          'electric_field',
          'electric_circuits',
          'magnetism',
          'electromagnetic_induction',
          'ac_circuits',
        ],
      },
      {
        id: 'waves_optics_hs',
        heLabel: 'גלים ואופטיקה',
        enLabel: 'Waves & Optics',
        concept_ids: [
          'geometric_optics_refraction',
          'em_waves',
          'waves_basics',
          'sound_waves',
          'doppler',
          'optics_geometric',
          'optics_physical',
        ],
      },
      {
        id: 'modern_physics_hs',
        heLabel: 'פיזיקה מודרנית',
        enLabel: 'Modern Physics',
        concept_ids: [
          'photoelectric_effect',
          'modern_physics_intro',
          'atomic_models',
          'nuclear_physics',
          'special_relativity',
        ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // UNIVERSITY PHYSICS 1 — Calculus-based mechanics
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'university_physics_1',
    heLabel: 'פיזיקה 1 — מכניקה',
    enLabel: 'Physics 1 — Mechanics',
    emoji: '⚙️',
    points_levels: ['university_physics_1'],
    concept_ids: UNI_PHYSICS_1_CONCEPTS,
    sections: [
      {
        id: 'kinematics_dynamics_uni',
        heLabel: 'קינמטיקה ודינמיקה',
        enLabel: 'Kinematics & Dynamics',
        concept_ids: [ 'kinematics_2d',
          'vectors_2d',
          'newton_laws' ],
      },
      {
        id: 'energy_momentum_uni',
        heLabel: 'אנרגיה ותנע',
        enLabel: 'Energy & Momentum',
        concept_ids: [ 'work_energy',
          'momentum' ],
      },
      {
        id: 'rigid_body_statics_uni',
        heLabel: 'גוף קשיח ושיווי משקל',
        enLabel: 'Rigid Body & Statics',
        concept_ids: [ 'rigid_body_torque_equilibrium' ],
      },
      {
        id: 'rotation_angular_momentum_uni',
        heLabel: 'סיבוב ותנע זוויתי',
        enLabel: 'Rotation & Angular Momentum',
        concept_ids: [ 'angular_momentum_particles' ],
      },
      {
        id: 'systems_of_particles_uni',
        heLabel: 'מערכות חלקיקים',
        enLabel: 'Systems of Particles',
        concept_ids: [ 'center_of_mass_uni' ],
      },
      {
        id: 'oscillations_uni',
        heLabel: 'תנודות',
        enLabel: 'Oscillations',
        concept_ids: [ 'harmonic_oscillation' ],
      },
      {
        id: 'fluids_uni',
        heLabel: 'פלואידים',
        enLabel: 'Fluids',
        concept_ids: [ 'fluids_hydrostatics' ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // UNIVERSITY PHYSICS 2 — Calculus-based E&M
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'university_physics_2',
    heLabel: 'פיזיקה 2 — חשמל ומגנטיות',
    enLabel: 'Physics 2 — E&M',
    emoji: '⚡',
    points_levels: ['university_physics_2'],
    concept_ids: UNI_PHYSICS_2_CONCEPTS,
    sections: [
      {
        id: 'electrostatics_uni',
        heLabel: 'אלקטרוסטטיקה',
        enLabel: 'Electrostatics',
        concept_ids: [ 'electrostatics',
          'electric_field_gauss',
          'electric_field' ],
      },
      {
        id: 'circuits_magnetism_uni',
        heLabel: 'מעגלים ומגנטיות',
        enLabel: 'Circuits & Magnetism',
        concept_ids: [ 'kirchhoff_laws',
          'magnetic_field_biot_savart',
          'ampere_law',
          'faraday_induction_uni' ],
      },
      {
        id: 'em_waves_optics_uni',
        heLabel: 'גלים אלקטרומגנטיים ואופטיקה',
        enLabel: 'EM Waves & Optics',
        concept_ids: [ 'maxwell_equations',
          'optics_geometric',
          'optics_physical' ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // מכינה — university prep bridge
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'makhina',
    heLabel: 'מכינה אקדמית',
    enLabel: 'University Prep (מכינה)',
    emoji: '🎓',
    points_levels: ['makhina'],
    concept_ids: MAKHINA_CONCEPTS,
    sections: [
      {
        id: 'calculus_intensive',
        heLabel: 'חשבון אינפינטסימלי',
        enLabel: 'Calculus Intensive',
        concept_ids: [
          'limits_intro',
          'limits_epsilon_delta',
          'derivatives_intro',
          'derivatives_chain_rule',
          'derivatives_trigonometric',
          'integrals_intro',
          'integrals_substitution_basic',
          'volumes_of_revolution',
          'derivatives_exponential_logarithm',
        ],
      },
      {
        id: 'linear_algebra_intro',
        heLabel: 'אלגברה לינארית',
        enLabel: 'Linear Algebra',
        concept_ids: [
          'la_vectors',
          'la_matrices',
          'la_diagonalization',
          'la_orthogonality',
          'la_determinants',
          'la_vector_spaces',
          'eigenvalues_eigenvectors',
        ],
      },
      {
        id: 'statistics_probability',
        heLabel: 'סטטיסטיקה והסתברות',
        enLabel: 'Statistics & Probability',
        concept_ids: [
          'statistics_descriptive',
          'probability_basic',
          'statistics_inference',
          'normal_distribution_z_scores',
        ],
      },
      {
        id: 'foundation',
        heLabel: 'יסודות',
        enLabel: 'Foundation',
        concept_ids: [
          'algebra_basics',
          'word_problems',
          'sequences_arithmetic',
          'sequences_geometric',
          'analytic_geometry',
          'trigonometry_identities',
          'fractions_and_ratios',
          'linear_equations_basics',
          'percentages_and_interest',
          'geometry_area_perimeter',
        ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // CALCULUS 1 — University (real numbers → Taylor, NO integrals at Technion)
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'calculus_1',
    heLabel: 'חדו״א 1',
    enLabel: 'Calculus 1',
    emoji: '∂',
    points_levels: ['calc1'],
    concept_ids: CALCULUS_1_CONCEPTS,
    sections: [
      {
        id: 'limits_continuity',
        heLabel: 'גבולות ורציפות',
        enLabel: 'Limits & Continuity',
        concept_ids: [ 'limits_intro',
          'continuity',
          'limits_epsilon_delta',
          'limits' ],
      },
      {
        id: 'derivatives_calc1',
        heLabel: 'נגזרות',
        enLabel: 'Derivatives',
        concept_ids: [
          'derivatives_intro',
          'derivatives_chain_rule',
          'derivatives_applications',
          'mean_value_theorem',
          'derivatives_rules',
        ],
      },
      {
        id: 'series_taylor',
        heLabel: 'טורים וטיילור',
        enLabel: 'Series & Taylor',
        concept_ids: [ 'sequences_limits',
          'taylor_formula' ],
      },
      {
        id: 'function_analysis_calc1',
        heLabel: 'ניתוח פונקציות',
        enLabel: 'Function Analysis',
        concept_ids: [
          'function_analysis_asymptotes',
          'optimization_problems',
          'derivatives_rules',
        ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // CALCULUS 2 — University (integrals + series + multivariable)
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'calculus_2',
    heLabel: 'חדו״א 2',
    enLabel: 'Calculus 2',
    emoji: '∫',
    points_levels: ['calculus_2'],
    concept_ids: CALCULUS_2_CONCEPTS,
    sections: [
      {
        id: 'integrals_calc2',
        heLabel: 'אינטגרלים',
        enLabel: 'Integrals',
        concept_ids: [
          'integrals_intro',
          'integration_substitution',
          'integration_by_parts',
          'definite_integrals',
          'integrals_techniques',
          'integrals_applications',
        ],
      },
      {
        id: 'series_calc2',
        heLabel: 'טורים',
        enLabel: 'Series',
        concept_ids: [ 'taylor_formula' ],
      },
      {
        id: 'multivariable_calc2',
        heLabel: 'חשבון רב-משתנים',
        enLabel: 'Multivariable Calculus',
        concept_ids: [ 'limits',
          'partial_derivatives',
          'double_integrals' ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // LINEAR ALGEBRA — University
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'linear_algebra',
    heLabel: 'אלגברה לינארית',
    enLabel: 'Linear Algebra',
    emoji: '📐',
    points_levels: ['la'],
    concept_ids: LINEAR_ALGEBRA_CONCEPTS,
    sections: [
      {
        id: 'systems_matrices',
        heLabel: 'מערכות ומטריצות',
        enLabel: 'Systems & Matrices',
        concept_ids: [
          'la_matrices',
          'la_determinants',
        ],
      },
      {
        id: 'vector_spaces',
        heLabel: 'מרחבים וקטוריים',
        enLabel: 'Vector Spaces',
        concept_ids: [
          'la_vectors',
          'la_vector_spaces',
          'la_matrices',
        ],
      },
      {
        id: 'eigenvalues_inner_product',
        heLabel: 'ערכים עצמיים ומכפלה פנימית',
        enLabel: 'Eigenvalues & Inner Products',
        concept_ids: [
          'la_diagonalization',
          'eigenvalues_eigenvectors',
          'la_eigenvalues',
          'la_orthogonality',
        ],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // STATISTICS & PROBABILITY — University
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'statistics_probability',
    heLabel: 'סטטיסטיקה והסתברות',
    enLabel: 'Statistics & Probability',
    emoji: '📊',
    points_levels: ['stats_prob'],
    concept_ids: STATS_PROB_CONCEPTS,
    sections: [
      {
        id: 'probability_foundations',
        heLabel: 'יסודות ההסתברות',
        enLabel: 'Probability Foundations',
        concept_ids: [
          'probability_basic',
          'probability_conditional_bayes',
          'distributions',
          'combinatorics',
          'statistics_descriptive',
          'descriptive_stats',
        ],
      },
      {
        id: 'continuous_distributions',
        heLabel: 'התפלגויות רציפות',
        enLabel: 'Continuous Distributions',
        concept_ids: [ 'normal_distribution_z_scores',
          'statistics_inference',
          'central_limit_theorem' ],
      },
      {
        id: 'statistical_inference',
        heLabel: 'הסקה סטטיסטית',
        enLabel: 'Statistical Inference',
        concept_ids: [
          'hypothesis_testing_intro',
          'hypothesis_testing',
          'hypothesis_testing_z_t',
          'confidence_intervals',
          'chi_square_goodness_of_fit',
          'anova_one_way',
          'chi_square_tests',
          'linear_regression_correlation',
          'linear_regression_least_squares',
          'correlation_coefficient',
        ],
      },
    ],
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// Convenience helpers
// ─────────────────────────────────────────────────────────────────────────────

/** Look up a category by id (supports legacy aliases) */
export function getCategoryById(id: string): CurriculumCategory | undefined {
  const canonical = CATEGORY_ID_ALIASES[id] ?? id;
  return CURRICULUM_CATEGORIES.find((c) => c.id === canonical);
}

/** All concept IDs in scope for a given points_level */
export function conceptIdsForLevel(level: PointsLevel): string[] {
  const cat = CURRICULUM_CATEGORIES.find((c) => c.points_levels.includes(level));
  return cat?.concept_ids ?? [];
}

/** Map from goal string (used in onboarding) to PointsLevel */
export const GOAL_TO_LEVEL: Record<string, PointsLevel> = {
  bagrut_math_3pt: '3pt',
  bagrut_math_4pt: '4pt',
  bagrut_math_5pt: '5pt',
  bagrut_physics: 'hs_physics',
  makhina: 'makhina',
  university_prep: 'makhina',
  calculus1: 'calc1',
  calculus_1: 'calc1',
  calculus_2: 'calculus_2',
  linear_algebra: 'la',
  university_physics_1: 'university_physics_1',
  university_physics_2: 'university_physics_2',
  statistics_probability: 'stats_prob',
};

/** Legacy category id aliases (old slugs → new canonical ids) */
export const CATEGORY_ID_ALIASES: Record<string, string> = {
  'math-hs-3': 'high_school_math_3pt',
  'math-hs-4': 'high_school_math_4pt',
  'math-hs-5': 'high_school_math_5pt',
  'physics-hs': 'hs_physics',
  calculus: 'calculus_1',
  'linear-algebra': 'linear_algebra',
};

/** UI subject slug → curriculum category id (canonical + all legacy aliases) */
export const SUBJECT_TO_CATEGORY: Record<string, string> = {
  // Canonical
  high_school_math_3pt: 'high_school_math_3pt',
  high_school_math_4pt: 'high_school_math_4pt',
  high_school_math_5pt: 'high_school_math_5pt',
  hs_physics: 'hs_physics',
  university_physics_1: 'university_physics_1',
  university_physics_2: 'university_physics_2',
  makhina: 'makhina',
  calculus_1: 'calculus_1',
  calculus_2: 'calculus_2',
  linear_algebra: 'linear_algebra',
  statistics_probability: 'statistics_probability',
  // Legacy / alias slugs
  high_school_math_3_points: 'high_school_math_3pt',
  high_school_math_4_points: 'high_school_math_4pt',
  high_school_math_5_points: 'high_school_math_5pt',
  'high-school-math-3-pts': 'high_school_math_3pt',
  'high-school-math-4-pts': 'high_school_math_4pt',
  'high-school-math-5-pts': 'high_school_math_5pt',
  'hs-math-3': 'high_school_math_3pt',
  'hs-math-4': 'high_school_math_4pt',
  'hs-math-5': 'high_school_math_5pt',
  hs_math_3: 'high_school_math_3pt',
  hs_math_4: 'high_school_math_4pt',
  hs_math_5: 'high_school_math_5pt',
  'math-hs-3': 'high_school_math_3pt',
  'math-hs-4': 'high_school_math_4pt',
  'math-hs-5': 'high_school_math_5pt',
  high_school_physics: 'hs_physics',
  'high-school-physics': 'hs_physics',
  physics_high_school: 'hs_physics',
  'physics-hs': 'hs_physics',
  hs_physics_5: 'hs_physics',
  physics_1: 'university_physics_1',
  physics_2: 'university_physics_2',
  calculus: 'calculus_1',
  'linear-algebra': 'linear_algebra',
  university_prep: 'makhina',
  physics_pre_university: 'makhina',
  math_pre_university: 'makhina',
};
