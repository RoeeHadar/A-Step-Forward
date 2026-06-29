/**
 * Curriculum category catalogue — aligned with Israeli Bagrut curriculum.
 *
 * Source: Gool.co.il course syllabi + Ministry of Education (Misrad HaChinuch)
 * questionnaire specs + past Bagrut papers (2019-2024).
 *
 * Each category maps to a distinct Bagrut track and carries:
 *   - `points_levels`       – which learner goal tags apply
 *   - `bagrut_questionnaires` – official questionnaire numbers (for agents)
 *   - `sections`            – chapters inside this track
 *   - `concept_ids`         – KG concept IDs covering this track's scope
 *
 * How depth adapts per level (see skill_atoms in kg-data.json):
 *   3pt  – practical, concrete, minimal theory; word problems; no calculus
 *   4pt  – includes proofs, parametric problems, wider trig/geometry
 *   5pt  – full analytic treatment, calculus, advanced conic sections
 *   hs_physics – all four Bagrut physics questionnaires
 */

export type PointsLevel =
  | '3pt'
  | '4pt'
  | '5pt'
  | 'hs_physics'
  | 'calc1'
  | 'la'
  | 'physics1';

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
// MATH — 3 UNITS
// Bagrut questionnaires: 801/182 (כיתה י׳), 802/381 (כיתה י״א), 803/382 (כיתה י״ב)
// ─────────────────────────────────────────────────────────────────────────────
const MATH_3PT_CONCEPTS = [
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

// ─────────────────────────────────────────────────────────────────────────────
// MATH — 4 UNITS
// Bagrut questionnaires: 484 / 485
// ─────────────────────────────────────────────────────────────────────────────
const MATH_4PT_CONCEPTS = [
  ...MATH_3PT_CONCEPTS,
  'fractions_algebraic',
  'factoring',
  'functions_exponential',
  'sequences_geometric',
  'quadrilaterals',
  'triangles_congruence',
  'circles',
  'combinatorics',
];

// ─────────────────────────────────────────────────────────────────────────────
// MATH — 5 UNITS
// Bagrut questionnaires: 581 (core), 807 (analytic geom, vectors, complex)
// ─────────────────────────────────────────────────────────────────────────────
const MATH_5PT_CONCEPTS = [
  ...MATH_4PT_CONCEPTS,
  'logarithms',
  'function_transformations',
  'trigonometry_identities',
  'trigonometry_equations',
  'analytic_geometry',
  'vectors_2d',
  'distributions',
  'limits',
  'derivatives_intro',
  'derivatives_rules',
  'derivatives_applications',
  'optimization_problems',
  'integrals_intro',
  'definite_integrals',
  'integrals_techniques',
  'integrals_applications',
];

// ─────────────────────────────────────────────────────────────────────────────
// PHYSICS — 5 UNITS
// Bagrut questionnaires: 036-361 (mechanics), 036-371 (electricity),
//                        radiation & matter, lab
// ─────────────────────────────────────────────────────────────────────────────
const PHYSICS_HS_CONCEPTS = [
  'units_measurement',
  'vectors_basics',
  'kinematics_1d',
  'kinematics_2d',
  'projectile_motion',
  'newton_laws',
  'friction',
  'circular_motion',
  'gravitation',
  'work_energy',
  'conservation_energy',
  'momentum',
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
  'electric_potential',
  'electric_circuits',
  'kirchhoff_laws',
  'magnetism',
  'electromagnetic_induction',
  'ac_circuits',
  'modern_physics_intro',
  'atomic_models',
  'nuclear_physics',
  'special_relativity',
];

// ─────────────────────────────────────────────────────────────────────────────
export const CURRICULUM_CATEGORIES: CurriculumCategory[] = [
  // ──────────────────────────────────────────────────────────────────────────
  // MATH 3pt
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'math-hs-3',
    heLabel: 'מתמטיקה לבגרות — 3 יחידות',
    enLabel: 'Bagrut Math — 3 Units',
    emoji: '📐',
    points_levels: ['3pt'],
    bagrut_questionnaires: ['801/182', '802/381', '803/382'],
    concept_ids: MATH_3PT_CONCEPTS,
    sections: [
      {
        id: 'sh801-algebra',
        heLabel: 'אלגברה יסודית',
        enLabel: 'Foundational Algebra',
        concept_ids: ['arithmetic', 'algebra_basics', 'equations_linear', 'equations_quadratic', 'exponents'],
      },
      {
        id: 'sh801-analytic-geo',
        heLabel: 'גיאומטריה אנליטית — ישר ופרבולה',
        enLabel: 'Analytic Geometry — Lines & Parabolas',
        concept_ids: ['analytic_geometry_basic', 'functions_linear'],
      },
      {
        id: 'sh801-sequences',
        heLabel: 'סדרות חשבוניות והנדסיות',
        enLabel: 'Arithmetic & Geometric Sequences',
        concept_ids: ['sequences_arithmetic', 'sequences_geometric'],
      },
      {
        id: 'sh801-trigonometry',
        heLabel: 'טריגונומטריה במישור',
        enLabel: 'Trigonometry (Plane)',
        concept_ids: ['trigonometry_ratios', 'geometry_basics'],
      },
      {
        id: 'sh801-stats',
        heLabel: 'סטטיסטיקה והסתברות',
        enLabel: 'Statistics & Probability',
        concept_ids: ['statistics_descriptive', 'probability_basic'],
      },
      {
        id: 'sh802-sequences-growth',
        heLabel: 'סדרות וגדילה',
        enLabel: 'Sequences & Discrete Growth',
        concept_ids: ['sequences_arithmetic', 'functions_quadratic'],
      },
      {
        id: 'sh802-trig-3d',
        heLabel: 'טריגונומטריה במרחב',
        enLabel: 'Trigonometry in Space',
        concept_ids: ['trigonometry_ratios'],
      },
      {
        id: 'sh802-normal-dist',
        heLabel: 'התפלגות נורמלית',
        enLabel: 'Normal Distribution',
        concept_ids: ['descriptive_stats', 'probability_basic'],
      },
      {
        id: 'sh803-word-problems',
        heLabel: 'בעיות מילוליות ואחוזים',
        enLabel: 'Word Problems & Percentages',
        concept_ids: ['word_problems', 'arithmetic'],
      },
      {
        id: 'sh803-analytic-geo',
        heLabel: 'גיאומטריה אנליטית — מעגל',
        enLabel: 'Analytic Geometry — Circles',
        concept_ids: ['analytic_geometry_basic', 'functions_linear'],
      },
      {
        id: 'sh803-functions-review',
        heLabel: 'פונקציות — חזרה ויישומים',
        enLabel: 'Functions — Review & Applications',
        concept_ids: ['functions_quadratic', 'functions_intro', 'functions_linear'],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // MATH 4pt
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'math-hs-4',
    heLabel: 'מתמטיקה לבגרות — 4 יחידות',
    enLabel: 'Bagrut Math — 4 Units',
    emoji: '📏',
    points_levels: ['4pt'],
    bagrut_questionnaires: ['484', '485'],
    concept_ids: MATH_4PT_CONCEPTS,
    sections: [
      {
        id: 'algebra-4pt',
        heLabel: 'אלגברה (עם שברים אלגבריים)',
        enLabel: 'Algebra (Algebraic Fractions)',
        concept_ids: ['algebra_basics', 'fractions_algebraic', 'factoring', 'equations_quadratic', 'inequalities'],
      },
      {
        id: 'functions-4pt',
        heLabel: 'פונקציות (כולל אקספוננציאלית)',
        enLabel: 'Functions (incl. Exponential)',
        concept_ids: ['functions_intro', 'functions_linear', 'functions_quadratic', 'functions_exponential'],
      },
      {
        id: 'geometry-4pt',
        heLabel: 'גיאומטריה (חפיפה ודמיון)',
        enLabel: 'Geometry (Congruence & Similarity)',
        concept_ids: ['geometry_basics', 'quadrilaterals', 'triangles_congruence', 'circles'],
      },
      {
        id: 'sequences-4pt',
        heLabel: 'סדרות (חשבוניות והנדסיות)',
        enLabel: 'Sequences (Arithmetic & Geometric)',
        concept_ids: ['sequences_arithmetic', 'sequences_geometric'],
      },
      {
        id: 'trigonometry-4pt',
        heLabel: 'טריגונומטריה',
        enLabel: 'Trigonometry',
        concept_ids: ['trigonometry_ratios'],
      },
      {
        id: 'analytic-geo-4pt',
        heLabel: 'גיאומטריה אנליטית',
        enLabel: 'Analytic Geometry',
        concept_ids: ['analytic_geometry_basic'],
      },
      {
        id: 'probability-4pt',
        heLabel: 'קומבינטוריקה והסתברות',
        enLabel: 'Combinatorics & Probability',
        concept_ids: ['combinatorics', 'probability_basic', 'descriptive_stats'],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // MATH 5pt
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'math-hs-5',
    heLabel: 'מתמטיקה לבגרות — 5 יחידות',
    enLabel: 'Bagrut Math — 5 Units',
    emoji: '🔢',
    points_levels: ['5pt'],
    bagrut_questionnaires: ['581', '807'],
    concept_ids: MATH_5PT_CONCEPTS,
    sections: [
      {
        id: 'algebra-5pt',
        heLabel: 'אלגברה — סדרות, משוואות, אי-שוויונים',
        enLabel: 'Algebra — Sequences, Equations, Inequalities',
        concept_ids: ['arithmetic', 'algebra_basics', 'equations_linear', 'equations_quadratic', 'inequalities', 'exponents', 'fractions_algebraic', 'factoring', 'word_problems', 'sequences_arithmetic', 'sequences_geometric'],
      },
      {
        id: 'functions-5pt',
        heLabel: 'פונקציות — סוגים ומאפיינים',
        enLabel: 'Functions — Types & Properties',
        concept_ids: ['functions_intro', 'functions_linear', 'functions_quadratic'],
      },
      {
        id: 'probability-5pt',
        heLabel: 'סטטיסטיקה, הסתברות קלאסית ובינומית',
        enLabel: 'Statistics, Classical & Binomial Probability',
        concept_ids: ['descriptive_stats', 'probability_basic', 'combinatorics', 'distributions'],
      },
      {
        id: 'geometry-5pt',
        heLabel: 'גיאומטריה — חפיפה, דמיון, מעגל',
        enLabel: 'Geometry — Congruence, Similarity, Circles',
        concept_ids: ['geometry_basics', 'quadrilaterals', 'triangles_congruence', 'circles'],
      },
      {
        id: 'trigonometry-5pt',
        heLabel: 'טריגונומטריה — זהויות ומשוואות',
        enLabel: 'Trigonometry — Identities & Equations',
        concept_ids: ['trigonometry_ratios', 'trigonometry_identities', 'trigonometry_equations'],
      },
      {
        id: 'calculus-5pt',
        heLabel: 'חשבון דיפרנציאלי — נגזרות וחקירת פונקציה',
        enLabel: 'Differential Calculus — Derivatives & Function Analysis',
        concept_ids: ['limits', 'continuity', 'derivatives_intro', 'derivatives_rules', 'derivatives_applications', 'optimization_problems', 'function_transformations'],
      },
      {
        id: 'integrals-5pt',
        heLabel: 'אינטגרלים — שטחים ונפחים',
        enLabel: 'Integrals — Areas & Volumes',
        concept_ids: ['integrals_intro', 'definite_integrals', 'integrals_techniques', 'integrals_applications'],
      },
      {
        id: 'analytic-geo-5pt',
        heLabel: 'גיאומטריה אנליטית — חתכי חרוט',
        enLabel: 'Analytic Geometry — Conic Sections',
        concept_ids: ['analytic_geometry_basic', 'analytic_geometry'],
      },
      {
        id: 'vectors-5pt',
        heLabel: 'וקטורים וטריגונומטריה במרחב',
        enLabel: 'Vectors & 3D Trigonometry',
        concept_ids: ['vectors_2d'],
      },
      {
        id: 'logarithms-5pt',
        heLabel: 'לוגריתמים וגדילה/דעיכה',
        enLabel: 'Logarithms & Growth/Decay',
        concept_ids: ['functions_exponential', 'logarithms'],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // PHYSICS — Bagrut 5 units
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'physics-hs',
    heLabel: 'פיזיקה לבגרות — 5 יחידות',
    enLabel: 'Bagrut Physics — 5 Units',
    emoji: '⚡',
    points_levels: ['hs_physics'],
    bagrut_questionnaires: ['036-361 (מכניקה)', '036-371 (חשמל)', 'קרינה וחומר', 'מעבדה'],
    concept_ids: PHYSICS_HS_CONCEPTS,
    sections: [
      {
        id: 'kinematics',
        heLabel: 'קינמטיקה — תנועה ללא כוחות',
        enLabel: 'Kinematics — Motion Without Forces',
        concept_ids: ['units_measurement', 'vectors_basics', 'kinematics_1d', 'kinematics_2d', 'projectile_motion'],
      },
      {
        id: 'dynamics',
        heLabel: 'דינמיקה — חוקי ניוטון',
        enLabel: 'Dynamics — Newton\'s Laws',
        concept_ids: ['newton_laws', 'friction', 'circular_motion', 'gravitation'],
      },
      {
        id: 'energy-momentum',
        heLabel: 'אנרגיה ותנע',
        enLabel: 'Energy & Momentum',
        concept_ids: ['work_energy', 'conservation_energy', 'momentum', 'collisions'],
      },
      {
        id: 'rotation-shm',
        heLabel: 'סיבוב ותנועה הרמונית',
        enLabel: 'Rotation & SHM',
        concept_ids: ['torque', 'static_equilibrium', 'rotational_kinematics', 'rotational_dynamics', 'simple_harmonic_motion'],
      },
      {
        id: 'electricity',
        heLabel: 'חשמל ומגנטיות (שאלון 036-371)',
        enLabel: 'Electricity & Magnetism (Q 036-371)',
        concept_ids: ['electrostatics', 'electric_field', 'electric_potential', 'electric_circuits', 'kirchhoff_laws', 'magnetism', 'electromagnetic_induction', 'ac_circuits'],
      },
      {
        id: 'radiation-matter',
        heLabel: 'קרינה וחומר — אופטיקה, גלים, פיזיקה מודרנית',
        enLabel: 'Radiation & Matter — Optics, Waves, Modern Physics',
        concept_ids: ['waves_basics', 'sound_waves', 'doppler', 'optics_geometric', 'optics_physical', 'modern_physics_intro', 'atomic_models', 'nuclear_physics', 'special_relativity'],
      },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // UNIVERSITY — Calculus 1 (חדו״א 1)
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'calculus',
    heLabel: 'חדו״א 1 (אוניברסיטה)',
    enLabel: 'Calculus 1 (University)',
    emoji: '∫',
    points_levels: ['calc1'],
    concept_ids: [
      'limits',
      'continuity',
      'derivatives_intro',
      'derivatives_rules',
      'derivatives_applications',
      'integrals_intro',
      'integrals_techniques',
      'definite_integrals',
      'integrals_applications',
    ],
    sections: [
      { id: 'limits', heLabel: 'גבולות', enLabel: 'Limits & Continuity' },
      { id: 'derivatives', heLabel: 'נגזרות', enLabel: 'Derivatives' },
      { id: 'integrals', heLabel: 'אינטגרלים', enLabel: 'Integrals' },
    ],
  },

  // ──────────────────────────────────────────────────────────────────────────
  // UNIVERSITY — Linear Algebra
  // ──────────────────────────────────────────────────────────────────────────
  {
    id: 'linear-algebra',
    heLabel: 'אלגברה לינארית (אוניברסיטה)',
    enLabel: 'Linear Algebra (University)',
    emoji: '🔲',
    points_levels: ['la'],
    concept_ids: [
      'la_vectors',
      'la_matrices',
      'la_determinants',
      'la_vector_spaces',
      'la_eigenvalues',
      'la_orthogonality',
      'la_diagonalization',
    ],
    sections: [
      { id: 'vectors', heLabel: 'וקטורים', enLabel: 'Vectors' },
      { id: 'matrices-and-systems', heLabel: 'מטריצות ומערכות', enLabel: 'Matrices & Systems' },
      { id: 'eigenvalues', heLabel: 'ערכים ווקטורים עצמיים', enLabel: 'Eigenvalues & Eigenvectors' },
    ],
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// Convenience helpers
// ─────────────────────────────────────────────────────────────────────────────

/** Look up a category by id */
export function getCategoryById(id: string): CurriculumCategory | undefined {
  return CURRICULUM_CATEGORIES.find((c) => c.id === id);
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
  calculus1: 'calc1',
  linear_algebra: 'la',
};
