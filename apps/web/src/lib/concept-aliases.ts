/**
 * Maps syllabus-aligned concept IDs to existing authored lesson / KG IDs.
 */
import { isConceptInLessonIndex } from './lesson-index';

export const CONCEPT_ID_ALIASES: Record<string, string> = {
  basic_probability: 'probability_basic',
  descriptive_statistics: 'statistics_descriptive',
  limits_intro: 'limits',
  derivatives_chain_rule: 'derivatives_rules',
  integrals_substitution_basic: 'integrals_techniques',
  work_energy_conservation: 'work_energy',
  work_energy_power: 'work_energy',
  momentum_impulse_collisions: 'momentum',
  circular_motion_gravitation: 'circular_motion',
  coulomb_law: 'electrostatics',
  electric_field_potential: 'electric_field',
  dc_circuits_kirchhoff: 'kirchhoff_laws',
  magnetic_force: 'magnetism',
  faraday_induction: 'electromagnetic_induction',
  geometric_optics_refraction: 'optics_geometric',
  geometric_optics: 'optics_geometric',
  hypothesis_testing_intro: 'hypothesis_testing',
  linear_regression_correlation: 'linear_regression_least_squares',
  newton_laws_general: 'newton_laws',
  function_analysis_extrema: 'derivatives_applications',
  function_analysis_asymptotes: 'derivatives_applications',
  optimization_word_problems: 'optimization_problems',
  derivatives_polynomial_rational: 'derivatives_rules',
  derivatives_trigonometric: 'derivatives_rules',
  derivatives_exponential_logarithm: 'derivatives_rules',
  integrals_polynomial_rational: 'integrals_applications',
  areas_between_curves: 'integrals_applications',
  volumes_of_revolution_basic: 'integrals_applications',
  volumes_of_revolution: 'integrals_applications',
  integrals_trigonometric: 'integrals_techniques',
  riemann_sums: 'riemann_integral_ftc',
  sequences_limits: 'sequences_arithmetic',
  eigenvalues_eigenvectors: 'la_eigenvalues',
  probability_conditional_bayes: 'probability_basic',
  trigonometry_plane_sine_cosine_law: 'trigonometry_ratios',
  hypothesis_testing_z_t: 'hypothesis_testing',
  correlation_coefficient: 'descriptive_stats',
  analytic_geometry_lines_circles: 'analytic_geometry',
  logarithmic_equations: 'logarithms',
  chi_square_goodness_of_fit: 'statistics_inference',
  central_limit_theorem: 'statistics_inference',
  // Close a catalog coverage gap with a level-appropriate authored lesson
  // (see docs/curriculum/scope-coverage-2026-07-19.md). Only aliased when the
  // target lesson's level matches the served track: modern_physics_intro is a
  // high-school lesson that already teaches the photoelectric effect.
  // NOT aliased (documented gaps / intentional stubs instead):
  //   - capacitors_parallel_plate, em_waves, normal_distribution_*: only
  //     university-level lessons exist; aliasing would over-serve HS learners.
  //   - extreme_value_theorem, intermediate_value_theorem,
  //     sequences_monotone_bounded, series_absolute_convergence,
  //     convergence_divergence_integrals: deliberate titled calc-1 stubs
  //     (guarded by learn-routes.test.ts) — leave as concept pages.
  photoelectric_effect: 'modern_physics_intro',
  // University track (KG syllabus ids → existing authored lessons)
  uni_functions_review: 'function_basics_uni',
  uni_limits: 'limits_epsilon_delta',
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

/** Dedupe key for catalog grids — distinct authored lessons must not collapse. */
export function catalogDedupeKey(conceptId: string): string {
  const raw = String(conceptId || '');
  // Track variants (`concept__4pt`) collapse to the canonical syllabus id.
  const dunder = raw.replace(/__(?:3pt|4pt|5pt|uni)$/, '');
  if (dunder !== raw) return dunder;
  // Track-named siblings (`limits_4pt`, `analytic_geometry_5pt`, `combinatorics_5pt`)
  const named = raw.replace(/_(?:3pt|4pt|5pt|uni)$/, '');
  if (
    named !== raw &&
    (named === 'limits' ||
      named === 'analytic_geometry' ||
      named === 'combinatorics' ||
      named === 'function_analysis' ||
      named === 'sequences')
  ) {
    return named === 'sequences' ? 'sequences_arithmetic' : named;
  }
  if (isConceptInLessonIndex(conceptId)) return conceptId;
  return resolveConceptAliasCanonical(conceptId);
}

/**
 * Remove duplicate catalog entries that resolve to the same authored lesson.
 * Prefers canonical KG ids over alias slugs when both appear in a track list.
 * Distinct authored lessons are never collapsed (e.g. vectors_2d vs vectors_plane).
 */
export function dedupeConceptIdsForCatalog(ids: string[]): string[] {
  const keyToPick = new Map<string, string>();
  for (const id of ids) {
    const key = catalogDedupeKey(id);
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
    const key = catalogDedupeKey(id);
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