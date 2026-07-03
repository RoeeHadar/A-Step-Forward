/**
 * Maps syllabus-aligned concept IDs to existing authored lesson / KG IDs.
 */
export const CONCEPT_ID_ALIASES: Record<string, string> = {
  basic_probability: 'probability_basic',
  descriptive_statistics: 'statistics_descriptive',
  limits_intro: 'limits',
  derivatives_chain_rule: 'derivatives_rules',
  integrals_substitution_basic: 'integrals_techniques',
  integration_substitution: 'integrals_techniques',
  trigonometric_identities: 'trigonometry_identities',
  trigonometric_equations: 'trigonometry_equations',
  vectors_2d: 'vectors_plane',
  vectors_dot_product_3d: 'vectors_plane',
  complex_numbers_de_moivre: 'complex_numbers',
  work_energy_conservation: 'work_energy',
  work_energy_power: 'work_energy',
  momentum_impulse_collisions: 'momentum',
  circular_motion_gravitation: 'circular_motion',
  coulomb_law: 'electrostatics',
  electrostatics_coulomb: 'electrostatics',
  electric_field_potential: 'electric_field',
  electric_field_gauss: 'electric_field',
  dc_circuits_kirchhoff: 'kirchhoff_laws',
  capacitors_parallel_plate: 'electrostatics',
  capacitors_dielectrics: 'electrostatics',
  magnetic_force: 'magnetism',
  faraday_induction: 'electromagnetic_induction',
  geometric_optics_refraction: 'optics_geometric',
  geometric_optics: 'optics_geometric',
  em_waves: 'waves_basics',
  photoelectric_effect: 'modern_physics_intro',
  linear_functions: 'functions_linear',
  linear_equations_one_variable: 'equations_linear',
  plane_trigonometry_right_triangle: 'trigonometry_ratios',
  hypothesis_testing_intro: 'hypothesis_testing',
  linear_regression_correlation: 'linear_regression_least_squares',
  normal_distribution_z_scores: 'descriptive_stats',
  normal_distribution_basics: 'descriptive_stats',
  newton_laws_general: 'newton_laws',
  vectors_kinematics_2d_3d: 'kinematics_2d',
  harmonic_oscillation: 'simple_harmonic_motion',
  angular_momentum_particles: 'angular_momentum',
  rigid_body_torque_equilibrium: 'torque',
  center_of_mass: 'newton_laws',
  fluids_hydrostatics: 'static_equilibrium',
  fluids_bernoulli: 'waves_basics',
  function_analysis_extrema: 'derivatives_applications',
  function_analysis_asymptotes: 'derivatives_applications',
  optimization_word_problems: 'optimization_problems',
  optimization_related_rates: 'derivatives_applications',
  derivatives_polynomial_rational: 'derivatives_rules',
  derivatives_trigonometric: 'derivatives_rules',
  derivatives_exponential_logarithm: 'derivatives_rules',
  derivatives_implicit: 'derivatives_rules',
  integrals_polynomial_rational: 'integrals_applications',
  areas_between_curves: 'integrals_applications',
  volumes_of_revolution_basic: 'integrals_applications',
  volumes_of_revolution: 'integrals_applications',
  integrals_trigonometric: 'integrals_techniques',
  integration_by_parts: 'integrals_techniques',
  integration_partial_fractions: 'integrals_techniques',
  riemann_sums: 'riemann_integral_ftc',
  sequences_limits: 'sequences_arithmetic',
  lhopital_rule: 'derivatives_applications',
  mean_value_theorem: 'derivatives_applications',
  limits_epsilon_delta: 'limits',
  continuity_uniform: 'continuity',
  taylor_formula: 'derivatives_applications',
  series_convergence_tests: 'sequences_geometric',
  power_series_radius: 'sequences_geometric',
  multivariable_limits: 'limits',
  partial_derivatives: 'derivatives_rules',
  gradient_directional_derivative: 'derivatives_rules',
  double_integrals: 'integrals_applications',
  linear_systems_gaussian_elimination: 'la_matrices',
  matrix_operations_inverse: 'la_matrices',
  determinants_cramer: 'la_determinants',
  vector_spaces_basis_dimension: 'la_vector_spaces',
  linear_transformations_kernel_image: 'la_vector_spaces',
  inner_product_gram_schmidt: 'la_orthogonality',
  orthogonal_matrices: 'la_orthogonality',
  eigenvalues_eigenvectors: 'la_eigenvalues',
  discrete_distributions_binomial_poisson: 'distributions',
  confidence_intervals: 'statistics_inference',
  probability_conditional_bayes: 'probability_basic',
  binomial_distribution_bernoulli: 'distributions',
  similar_triangles: 'triangles_congruence',
  euclidean_geometry_circles: 'circles',
  analytic_geometry_conics: 'analytic_geometry',
  trigonometry_plane_sine_cosine_law: 'trigonometry_ratios',
  exponential_growth_decay_models: 'functions_exponential',
  percentages_applications: 'arithmetic',
  scatter_plot_correlation_intro: 'descriptive_stats',
  pythagorean_theorem: 'geometry_basics',
  circle_area_circumference: 'circles',
  '3d_solids_volume': 'geometry_basics',
  spatial_reasoning: 'geometry_basics',
  quadratic_model_fitting: 'functions_quadratic',
  linear_programming_two_variables: 'functions_linear',
  mathematical_induction: 'sequences_arithmetic',
  magnetic_field_biot_savart: 'magnetism',
  ampere_law: 'magnetism',
  maxwell_equations: 'electromagnetic_induction',
  em_waves_propagation: 'waves_basics',
  interference_diffraction: 'optics_physical',
  hypothesis_testing_z_t: 'hypothesis_testing',
  linear_regression_least_squares: 'descriptive_stats',
  correlation_coefficient: 'descriptive_stats',
  analytic_geometry_lines_circles: 'analytic_geometry',
  logarithmic_equations: 'logarithms',
  chi_square_goodness_of_fit: 'statistics_inference',
  central_limit_theorem: 'statistics_inference',
  // University track (KG syllabus ids → existing authored lessons)
  uni_functions_review: 'function_basics_uni',
  uni_limits: 'limits',
  uni_derivatives: 'derivatives_intro',
  uni_derivative_applications: 'derivatives_applications',
  uni_integrals: 'integrals_intro',
  uni_integration_techniques: 'integrals_techniques',
  uni_applications_integrals: 'integrals_applications',
  uni_sequences_series: 'series_convergence_tests',
  uni_vectors: 'vectors_basics',
  uni_kinematics: 'kinematics_1d',
  uni_newtonian_mechanics: 'newton_laws',
  uni_work_energy: 'work_energy',
  uni_momentum: 'momentum',
  uni_rigid_body: 'rigid_body_dynamics',
  uni_oscillations: 'simple_harmonic_motion',
  uni_fluids: 'fluids_bernoulli',
  uni_thermodynamics: 'thermodynamics_makhina',
  uni_multivariable: 'multivariable_limits',
  uni_partial_derivatives: 'partial_derivatives',
  uni_multiple_integrals: 'double_integrals',
  uni_vector_fields: 'partial_derivatives',
  uni_line_integrals: 'double_integrals',
  uni_electric_fields: 'electric_field_gauss',
  uni_potential: 'electric_potential',
  uni_capacitance: 'capacitors_dielectrics',
  uni_dc_circuits: 'kirchhoff_laws',
  uni_magnetic_fields: 'magnetism',
  uni_induction: 'faraday_induction_uni',
  uni_ac_circuits: 'ac_circuits',
  uni_maxwell: 'maxwell_equations',
  uni_em_waves: 'em_waves_propagation',
  uni_optics: 'optics_physical',
  uni_quantum_intro: 'modern_physics_intro',
};

/** True when this catalog id is an alias slug (not the canonical lesson/KG id). */
export function isAliasConceptId(conceptId: string): boolean {
  return conceptId in CONCEPT_ID_ALIASES;
}

/**
 * Remove duplicate catalog entries that resolve to the same authored lesson.
 * Prefers canonical KG ids over alias slugs when both appear in a track list.
 */
export function dedupeConceptIdsForCatalog(ids: string[]): string[] {
  const keyToPick = new Map<string, string>();
  for (const id of ids) {
    const key = resolveConceptAliasCanonical(id);
    const current = keyToPick.get(key);
    if (!current) {
      keyToPick.set(key, id);
      continue;
    }
    const idIsAlias = isAliasConceptId(id);
    const currentIsAlias = isAliasConceptId(current);
    if (!idIsAlias && currentIsAlias) {
      keyToPick.set(key, id);
    } else if (id === key && current !== key) {
      keyToPick.set(key, id);
    }
  }
  const picked = new Set(keyToPick.values());
  const seen = new Set<string>();
  const out: string[] = [];
  for (const id of ids) {
    if (!picked.has(id)) continue;
    const key = resolveConceptAliasCanonical(id);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(id);
  }
  return out;
}

/** True when two catalog ids resolve to the same authored lesson / canonical id. */
export function catalogIdsCollide(a: string, b: string): boolean {
  return resolveConceptAliasCanonical(a) === resolveConceptAliasCanonical(b);
}

export function resolveConceptAlias(conceptId: string): string {
  return CONCEPT_ID_ALIASES[conceptId] ?? conceptId;
}

/** Follow alias chain to the terminal lesson / KG id (cycle-safe). */
export function resolveConceptAliasCanonical(conceptId: string): string {
  let cur = conceptId;
  const seen = new Set<string>();
  while (CONCEPT_ID_ALIASES[cur] && !seen.has(cur)) {
    seen.add(cur);
    cur = CONCEPT_ID_ALIASES[cur]!;
  }
  return cur;
}