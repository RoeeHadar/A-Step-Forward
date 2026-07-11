/**
 * Pick foundational self-assessment concepts from onboarding answers.
 * Avoids university-level topics for typical high-school learners.
 */

type GoalKey =
  | 'bagrut_math_3'
  | 'bagrut_math_4'
  | 'bagrut_math_5'
  | 'bagrut_physics'
  | 'calculus1'
  | 'linear_algebra'
  | 'university_prep'
  | 'other'
  | '';

const FOUNDATIONAL_BY_GOAL: Partial<Record<GoalKey, string[]>> = {
  bagrut_math_3: [
    'arithmetic',
    'algebra_basics',
    'equations_linear',
    'equations_quadratic',
    'functions_linear',
    'geometry_basics',
    'trigonometry_ratios',
    'probability_basic',
  ],
  bagrut_math_4: [
    'algebra_basics',
    'equations_quadratic',
    'functions_quadratic',
    'factoring',
    'triangles_congruence',
    'circles',
    'trigonometry_ratios',
    'combinatorics',
  ],
  bagrut_math_5: [
    'equations_quadratic',
    'functions_quadratic',
    'logarithms',
    'trigonometry_ratios',
    'trigonometry_identities',
    'limits',
    'derivatives_intro',
    'integrals_intro',
  ],
  bagrut_physics: [
    'units_measurement',
    'kinematics_1d',
    'newton_laws',
    'work_energy',
    'electrostatics',
    'electric_circuits',
    'waves_basics',
    'optics_geometric',
  ],
  calculus1: [
    'limits',
    'continuity',
    'derivatives_intro',
    'derivatives_rules',
    'integrals_intro',
    'definite_integrals',
  ],
  linear_algebra: ['la_vectors', 'la_matrices', 'la_determinants', 'la_eigenvalues'],
  university_prep: [
    'algebra_basics',
    'equations_quadratic',
    'functions_quadratic',
    'trigonometry_ratios',
    'limits',
    'derivatives_intro',
  ],
};

const ADULT_BY_GOAL: Record<string, string[]> = {
  bagrut_math: [
    'arithmetic',
    'algebra_basics',
    'equations_quadratic',
    'functions_quadratic',
    'geometry_basics',
    'trigonometry_ratios',
  ],
  bagrut_physics: [
    'units_measurement',
    'kinematics_1d',
    'newton_laws',
    'work_energy',
    'electrostatics',
    'waves_basics',
  ],
  university_math: [
    'algebra_basics',
    'functions_quadratic',
    'trigonometry_ratios',
    'limits',
    'derivatives_intro',
  ],
  university_physics: [
    'units_measurement',
    'kinematics_1d',
    'newton_laws',
    'work_energy',
    'electrostatics',
    'electric_circuits',
  ],
  general_improvement: [
    'arithmetic',
    'algebra_basics',
    'equations_linear',
    'functions_intro',
    'geometry_basics',
  ],
};

const PHYSICS_BASICS = [
  'units_measurement',
  'kinematics_1d',
  'newton_laws',
  'work_energy',
  'electrostatics',
  'waves_basics',
];

const MATH_BASICS = [
  'arithmetic',
  'algebra_basics',
  'equations_linear',
  'functions_linear',
  'geometry_basics',
];

export function resolveSelfScoreConceptIds(input: {
  goal: GoalKey;
  adultGoal?: string;
  isAdultLearner: boolean;
  subjects: string[];
  gradeLevel: string;
  pointsGroup: string;
  max?: number;
}): string[] {
  const max = input.max ?? 8;
  let ids: string[] = [];

  if (input.isAdultLearner && input.adultGoal) {
    ids = ADULT_BY_GOAL[input.adultGoal] ?? MATH_BASICS;
  } else if (input.goal && input.goal !== 'other') {
    ids = FOUNDATIONAL_BY_GOAL[input.goal] ?? MATH_BASICS;
  } else {
    ids = input.subjects.includes('math') ? [...MATH_BASICS] : [];
    if (input.subjects.includes('physics')) {
      ids = [...ids, ...PHYSICS_BASICS.slice(0, 4)];
    }
  }

  // Grade 10 — bias toward earlier foundations within the track
  if (input.gradeLevel === '10' && input.subjects.includes('math')) {
    ids = [
      'arithmetic',
      'algebra_basics',
      'equations_linear',
      'functions_linear',
      'geometry_basics',
      ...ids,
    ];
  }

  // Physics-only HS without math goal
  if (
    input.subjects.includes('physics') &&
    !input.subjects.includes('math') &&
    !input.goal.startsWith('bagrut_math')
  ) {
    ids = [...PHYSICS_BASICS, ...ids];
  }

  return [...new Set(ids)].slice(0, max);
}
