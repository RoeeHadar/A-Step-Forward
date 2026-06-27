#!/usr/bin/env node
/**
 * backfill-question-levels.mjs
 *
 * Backfills points_level_min on lesson questions based on:
 *   1. The lesson's math_track (if "4pt" or "5pt" only → set base min level)
 *   2. The KG concept's points_levels
 *   3. Question difficulty heuristic (hard → one level higher than base)
 *
 * This is a quick offline script that runs without an API key.
 * It enriches all lesson JSONs that don't yet have points_level_min on questions.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LESSONS_DIR = path.join(__dirname, 'seed_data', 'lessons');
const KG_JSON = path.join(__dirname, '..', 'apps', 'web', 'src', 'lib', 'kg-data.json');

const kg = JSON.parse(fs.readFileSync(KG_JSON, 'utf-8'));
const kgById = Object.fromEntries(kg.concepts.map(c => [c.id, c]));

// Which skill atoms are 5pt-only?
const FIVE_PT_ATOMS = new Set([
  // Calculus
  'chain_rule', 'product_rule', 'quotient_rule', 'implicit_differentiation',
  'L_hopital', 'limit_definition_computational', 'second_derivative_test',
  'curve_sketching', 'optimization_calculus', 'tangent_line_equation',
  'physical_interpretation_derivative', 'indefinite_integral', 'definite_integral',
  'ftc_1', 'ftc_2', 'integration_by_parts', 'integration_by_substitution',
  'area_between_curves', 'separation_of_variables',
  // Advanced algebra
  'logarithm_laws', 'exponential_equations', 'complex_numbers',
  'parametric_equations', 'vectors_2d', 'vectors_3d', 'dot_product', 'cross_product',
  'matrix_multiplication', 'eigenvalue', 'determinant',
  'bayes_theorem', 'binomial_distribution', 'normal_distribution',
  // Advanced geometry
  'tangent_discriminant', 'parabola_line_intersection', 'algebraic_proofs',
  'parametric_quadratics', 'optimization_word_problem',
]);

// Which skill atoms are 4pt+ (not available at 3pt)?
const FOUR_PT_ATOMS = new Set([
  'completing_the_square', 'vertex_form', 'range_quadratic', 'quadratic_inequalities',
  'factoring_quadratics', 'derivative_geometric_meaning', 'derivative_from_definition',
  'derivative_polynomial', 'sign_analysis', 'factor_quadratic',
  'logarithm_laws', 'logarithm_solving', 'circle_equation', 'tangent_to_circle',
  'recursive_sequence', 'conditional_probability', 'combinatorics_advanced',
  'discriminant_condition',
]);

// Level ordering
const LEVEL_ORDER = ['3pt', '4pt', '5pt', 'hs_physics', 'calc1', 'la'];
function levelIdx(l) { return LEVEL_ORDER.indexOf(l); }

function inferQuestionLevel(q, baseLevelMin) {
  // If already set, don't override
  if (q.points_level_min) return q.points_level_min;

  const atoms = q.skill_atoms ?? [];

  // Check 5pt atoms first
  if (atoms.some(a => FIVE_PT_ATOMS.has(a))) return '5pt';

  // Check 4pt atoms
  if (atoms.some(a => FOUR_PT_ATOMS.has(a))) {
    return levelIdx(baseLevelMin) >= levelIdx('4pt') ? baseLevelMin : '4pt';
  }

  // Apply difficulty bump: hard question at base level → next level
  if (q.difficulty === 'hard' && baseLevelMin === '3pt') return '4pt';

  return baseLevelMin;
}

function getLessonBaseLevel(lesson, kgConcept) {
  const mathTrack = lesson.math_track ?? [];

  // If lesson math_track starts at 4pt or 5pt
  if (mathTrack.includes('4pt') && !mathTrack.includes('3pt')) return '4pt';
  if (mathTrack.includes('5pt') && !mathTrack.includes('4pt') && !mathTrack.includes('3pt')) return '5pt';

  // Fallback to KG points_levels
  const kgLevels = kgConcept?.points_levels ?? [];
  if (kgLevels.length > 0) {
    // Take the lowest level
    for (const l of LEVEL_ORDER) {
      if (kgLevels.includes(l)) return l;
    }
  }

  return '3pt'; // default
}

const files = fs.readdirSync(LESSONS_DIR).filter(f => f.endsWith('.json'));
let totalUpdated = 0;

for (const file of files) {
  const fp = path.join(LESSONS_DIR, file);
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  const kgConcept = kgById[lesson.concept_id];
  const baseLevelMin = getLessonBaseLevel(lesson, kgConcept);

  let changed = false;
  if (lesson.questions) {
    for (const q of lesson.questions) {
      const newLevel = inferQuestionLevel(q, baseLevelMin);
      if (newLevel !== q.points_level_min) {
        q.points_level_min = newLevel;
        changed = true;
        totalUpdated++;
      }
    }
  }

  if (changed) {
    fs.writeFileSync(fp, JSON.stringify(lesson, null, 2) + '\n');
    console.log(`✓ ${lesson.concept_id}: ${lesson.questions?.length ?? 0} questions backfilled`);
  }
}

console.log(`\nDone. ${totalUpdated} question level annotations written.`);
