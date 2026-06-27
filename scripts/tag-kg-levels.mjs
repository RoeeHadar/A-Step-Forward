#!/usr/bin/env node
/**
 * Adds `points_levels` to every KG concept and removes out-of-scope entries
 * (Physics 2 EM/optics/quantum, Calculus 2/3 multivariable).
 *
 * Usage: node scripts/tag-kg-levels.mjs
 *
 * points_levels values:
 *   3pt         – Bagrut Math 3 units
 *   4pt         – Bagrut Math 4 units
 *   5pt         – Bagrut Math 5 units
 *   hs_physics  – Bagrut Physics (5 units)
 *   calc1       – University Calculus 1
 *   la          – University Linear Algebra
 *   physics1    – University Physics 1 (mechanics + thermo)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const KG_FILE = path.join(ROOT, 'apps', 'web', 'src', 'lib', 'kg-data.json');

// ── Level tags ────────────────────────────────────────────────────────────────
const LEVELS = /** @type {Record<string, string[]>} */ ({
  // ── Math – High School ────────────────────────────────────────────────────
  arithmetic:              ['3pt', '4pt', '5pt'],
  algebra_basics:          ['3pt', '4pt', '5pt'],
  equations_linear:        ['3pt', '4pt', '5pt'],
  equations_quadratic:     ['3pt', '4pt', '5pt'],
  fractions_algebraic:     ['4pt', '5pt'],
  exponents:               ['3pt', '4pt', '5pt'],
  factoring:               ['4pt', '5pt'],
  inequalities:            ['3pt', '4pt', '5pt'],
  word_problems:           ['3pt', '4pt', '5pt'],
  functions_intro:         ['3pt', '4pt', '5pt'],
  functions_linear:        ['3pt', '4pt', '5pt'],
  functions_quadratic:     ['3pt', '4pt', '5pt'],
  functions_exponential:   ['4pt', '5pt'],
  logarithms:              ['5pt'],
  function_transformations:['5pt'],
  trigonometry_ratios:     ['3pt', '4pt', '5pt'],
  trigonometry_identities: ['5pt'],
  trigonometry_equations:  ['5pt'],
  geometry_basics:         ['3pt', '4pt', '5pt'],
  quadrilaterals:          ['4pt', '5pt'],
  triangles_congruence:    ['4pt', '5pt'],
  circles:                 ['4pt', '5pt'],
  analytic_geometry_basic: ['3pt', '4pt', '5pt'],
  analytic_geometry:       ['5pt'],
  vectors_2d:              ['5pt'],
  sequences_arithmetic:    ['3pt', '4pt', '5pt'],
  sequences_geometric:     ['4pt', '5pt'],
  statistics_descriptive:  ['3pt', '4pt', '5pt'],
  probability_basic:       ['3pt', '4pt', '5pt'],
  combinatorics:           ['4pt', '5pt'],
  descriptive_stats:       ['3pt', '4pt', '5pt'],
  distributions:           ['5pt'],
  hypothesis_testing:      ['calc1'],
  limits:                  ['5pt'],
  continuity:              ['5pt', 'calc1'],
  derivatives_intro:       ['5pt'],
  derivatives_rules:       ['5pt'],
  derivatives_applications:['5pt'],
  optimization_problems:   ['5pt'],
  integrals_intro:         ['5pt'],
  integrals_techniques:    ['5pt'],
  definite_integrals:      ['5pt'],
  integrals_applications:  ['5pt'],
  differential_equations_intro: ['calc1'],

  // ── Math – University ─────────────────────────────────────────────────────
  complex_numbers:          ['calc1', 'la'],
  uni_functions_review:     ['calc1'],
  uni_limits:               ['calc1'],
  uni_derivatives:          ['calc1'],
  uni_derivative_applications: ['calc1'],
  uni_integrals:            ['calc1'],
  uni_integration_techniques: ['calc1'],
  uni_applications_integrals: ['calc1'],
  uni_sequences_series:     ['calc1'],

  // ── Linear Algebra ────────────────────────────────────────────────────────
  la_vectors:       ['la'],
  la_matrices:      ['la'],
  la_determinants:  ['la'],
  la_vector_spaces: ['la'],
  la_eigenvalues:   ['la'],
  la_orthogonality: ['la'],
  la_diagonalization: ['la'],

  // ── Physics – High School (Bagrut 5pt) ───────────────────────────────────
  units_measurement:        ['hs_physics'],
  vectors_basics:           ['hs_physics'],
  kinematics_1d:            ['hs_physics'],
  kinematics_2d:            ['hs_physics'],
  projectile_motion:        ['hs_physics'],
  newton_laws:              ['hs_physics'],
  friction:                 ['hs_physics'],
  circular_motion:          ['hs_physics'],
  work_energy:              ['hs_physics'],
  power:                    ['hs_physics'],
  conservation_energy:      ['hs_physics'],
  momentum:                 ['hs_physics'],
  collisions:               ['hs_physics'],
  rotational_kinematics:    ['hs_physics'],
  rotational_dynamics:      ['hs_physics'],
  torque:                   ['hs_physics'],
  angular_momentum:         ['hs_physics'],
  static_equilibrium:       ['hs_physics'],
  modern_physics_intro:     ['hs_physics'],
  atomic_models:            ['hs_physics'],
  nuclear_physics:          ['hs_physics'],
  special_relativity:       ['hs_physics'],
  ac_circuits:              ['hs_physics'],
  kirchhoff_laws:           ['hs_physics'],
  gravitation:              ['hs_physics'],
  simple_harmonic_motion:   ['hs_physics'],
  waves_basics:             ['hs_physics'],
  sound_waves:              ['hs_physics'],
  doppler:                  ['hs_physics'],
  optics_geometric:         ['hs_physics'],
  optics_physical:          ['hs_physics'],
  electrostatics:           ['hs_physics'],
  electric_field:           ['hs_physics'],
  electric_potential:       ['hs_physics'],
  electric_circuits:        ['hs_physics'],
  kirchhoff_laws:           ['hs_physics'],
  magnetism:                ['hs_physics'],
  electromagnetic_induction:['hs_physics'],
  ac_circuits:              ['hs_physics'],
  modern_physics_intro:     ['hs_physics'],
  nuclear_physics:          ['hs_physics'],
  special_relativity:       ['hs_physics'],
  atomic_models:            ['hs_physics'],

  // ── Physics – University Year 1 (mechanics + thermodynamics) ─────────────
  uni_vectors:           ['physics1'],
  uni_kinematics:        ['physics1'],
  uni_newtonian_mechanics: ['physics1'],
  uni_work_energy:       ['physics1'],
  uni_momentum:          ['physics1'],
  uni_rigid_body:        ['physics1'],
  uni_oscillations:      ['physics1'],
  uni_fluids:            ['physics1'],
  uni_thermodynamics:    ['physics1'],
});

// Concepts to remove entirely (Physics 2 EM/optics + Calculus 2/3)
const REMOVE = new Set([
  // Physics 2 – electromagnetism, optics, quantum
  'uni_electric_fields', 'uni_potential', 'uni_capacitance', 'uni_dc_circuits',
  'uni_magnetic_fields', 'uni_induction', 'uni_ac_circuits',
  'uni_maxwell', 'uni_em_waves', 'uni_optics', 'uni_quantum_intro',
  // Calculus 2/3 – multivariable
  'uni_multivariable', 'uni_partial_derivatives', 'uni_multiple_integrals',
  'uni_vector_fields', 'uni_line_integrals',
]);

// ── Process ───────────────────────────────────────────────────────────────────
const raw = JSON.parse(fs.readFileSync(KG_FILE, 'utf-8'));

const filtered = raw.concepts
  .filter((c) => !REMOVE.has(c.id))
  .map((c) => ({
    ...c,
    points_levels: LEVELS[c.id] ?? [],
  }));

const removedIds = new Set(raw.concepts.filter((c) => REMOVE.has(c.id)).map((c) => c.id));

const byId = Object.fromEntries(filtered.map((c) => [c.id, c]));

// Clean prereqs that point to removed concepts
for (const c of filtered) {
  c.prerequisites = (c.prerequisites ?? []).filter((p) => !removedIds.has(p));
}

const prereqMap = Object.fromEntries(filtered.map((c) => [c.id, c.prerequisites]));

const missing = filtered.filter((c) => c.points_levels.length === 0).map((c) => c.id);
if (missing.length > 0) {
  console.warn('⚠  Concepts with NO points_levels assigned (add to LEVELS map):', missing.join(', '));
}

fs.writeFileSync(KG_FILE, JSON.stringify({ concepts: filtered, prereqMap, byId }, null, 2));

console.log(`✅ Updated ${filtered.length} concepts (removed ${REMOVE.size} out-of-scope)`);
console.log(`   Removed: ${[...REMOVE].join(', ')}`);
