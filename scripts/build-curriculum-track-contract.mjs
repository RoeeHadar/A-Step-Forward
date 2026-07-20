#!/usr/bin/env node
/**
 * Build curriculum-track-contract v2 from the live lesson corpus + grill #2 rules.
 * Usage: node scripts/build-curriculum-track-contract.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const OUT = path.join(ROOT, 'scripts/seed_data/curriculum-track-contract.json');

const FIRST_WAVE = [
  'equations_quadratic',
  'functions_quadratic',
  'equations_linear',
  'functions_linear',
  'factoring',
  'algebra_basics',
  'inequalities',
  'functions_intro',
];

/** MoE-core bases that must be single-track (from multi-track inventory + first wave + scope map). */
const MOE_CORE = [
  ...FIRST_WAVE,
  'algebra_review',
  'analytic_geometry',
  'circle_area_circumference',
  'circles',
  'combinatorics',
  'definite_integrals',
  'derivatives_applications',
  'descriptive_stats',
  'euclidean_geometry_circles',
  'exponents',
  'fractions_algebraic',
  'fractions_and_ratios',
  'function_transformations',
  'functions_exponential',
  'geometry_area_perimeter',
  'linear_equations_basics',
  'linear_equations_one_variable',
  'linear_functions',
  'logarithms',
  'normal_distribution_basics',
  'normal_distribution_z_scores',
  'plane_trigonometry_right_triangle',
  'pythagorean_theorem',
  'quadrilaterals',
  'sample_space',
  'sequences_arithmetic',
  'sequences_geometric',
  'similar_triangles',
  'systems_linear_equations',
  'triangles_congruence',
  'trigonometry_equations',
  'trigonometry_identities',
  'trigonometry_ratios',
  'vectors_2d',
  'word_problems',
  'sequences_5pt',
  'limits_4pt',
  'limits_5pt',
  'function_analysis_4pt',
  'function_analysis_5pt',
  'probability_basics_3pt',
  'probability_conditional_3pt',
  'probability_basic',
  'combinatorics_5pt',
  'complex_numbers_5pt',
  'mathematical_induction',
  'analytic_geometry_4pt',
  'analytic_geometry_5pt',
  'linear_programming',
  'quadratic_model_fitting',
  'spatial_reasoning',
  '3d_solids_volume',
  'percentages_and_interest',
  'percentages_applications',
  'basic_statistics_3pt',
  'linear_regression_3pt',
].filter((v, i, a) => a.indexOf(v) === i);

const UNI_BRIDGE = [
  ...FIRST_WAVE,
  'limits_epsilon_delta',
  'function_basics_uni',
  'derivatives_intro',
  'integrals_intro',
  'la_vectors',
  'mean_value_theorem',
];

function loadLessons() {
  return fs
    .readdirSync(DIR)
    .filter((f) => f.endsWith('.json'))
    .map((f) => {
      const lesson = JSON.parse(fs.readFileSync(path.join(DIR, f), 'utf8'));
      return { file: f, id: lesson.concept_id || f.replace(/\.json$/, ''), lesson };
    });
}

function canonicalBase(id) {
  return String(id || '')
    .replace(/__(?:3pt|4pt|5pt|uni|university|makhina)$/, '')
    .replace(/_(?:3pt|4pt|5pt)$/, '');
}

function existsBase(entries, base) {
  return entries.some((e) => canonicalBase(e.id) === base || e.id === base);
}

const entries = loadLessons();

const hsPhysics = entries
  .filter(
    (e) =>
      e.lesson.subject === 'physics' &&
      e.lesson.level === 'high_school' &&
      !(e.lesson.math_track || []).includes('makhina') &&
      !/makhina/.test(e.id),
  )
  .map((e) => canonicalBase(e.id))
  .filter((v, i, a) => a.indexOf(v) === i)
  .sort();

const uniPhysics = entries
  .filter(
    (e) =>
      e.lesson.subject === 'physics' &&
      e.lesson.level === 'university' &&
      !(e.lesson.math_track || []).includes('makhina'),
  )
  .map((e) => canonicalBase(e.id))
  .filter((v, i, a) => a.indexOf(v) === i)
  .sort();

const makhina = entries
  .filter(
    (e) =>
      (e.lesson.math_track || []).includes('makhina') ||
      /makhina/.test(e.id) ||
      e.lesson.subject === 'makhina',
  )
  .map((e) => e.id)
  .filter((v, i, a) => a.indexOf(v) === i)
  .sort();

const moePresent = MOE_CORE.filter((b) => existsBase(entries, b));

/** After fan-out, every moe-core concept that currently multi-serves 3/4/5 must own each served track. */
function tracksNeededForBase(base) {
  const hits = entries.filter((e) => canonicalBase(e.id) === base || e.id === base);
  const set = new Set();
  for (const h of hits) {
    for (const t of h.lesson.math_track || []) {
      if (t === '3pt' || t === '4pt' || t === '5pt') set.add(t);
    }
    if (/__(?:3pt|4pt|5pt)$/.test(h.id) || /_(?:3pt|4pt|5pt)$/.test(h.id)) {
      const m = h.id.match(/(?:__|_)(3pt|4pt|5pt)$/);
      if (m) set.add(m[1]);
    }
  }
  if (FIRST_WAVE.includes(base)) {
    set.add('3pt');
    set.add('4pt');
    set.add('5pt');
  }
  // Dedicated track files already named *_4pt / *_5pt
  if (/_4pt$/.test(base) || base.endsWith('_4pt')) set.add('4pt');
  if (/_5pt$/.test(base) || base.endsWith('_5pt')) set.add('5pt');
  if (/_3pt$/.test(base)) set.add('3pt');
  return [...set];
}

const required_basics = { '3pt': [], '4pt': [], '5pt': [], university: [] };
for (const base of moePresent) {
  // Skip ids that ARE already track-specific filenames as required under wrong track
  if (/__(?:3pt|4pt|5pt|uni)$/.test(base)) continue;
  const needed = tracksNeededForBase(base);
  for (const t of needed) {
    if (!required_basics[t].includes(base)) required_basics[t].push(base);
  }
}
for (const b of UNI_BRIDGE) {
  if (existsBase(entries, b) && !required_basics.university.includes(b)) {
    required_basics.university.push(b);
  }
}
for (const k of Object.keys(required_basics)) required_basics[k].sort();

const prev = JSON.parse(fs.readFileSync(OUT, 'utf8'));

const contract = {
  version: 2,
  description:
    'Grill #2 SoT: MoE-core math + HS physics + makhina track ownership, denylists, facet checklists.',
  required_basics,
  physics_required: {
    hs_physics: hsPhysics,
    university: uniPhysics,
  },
  makhina_required: {
    makhina,
  },
  moe_core_concepts: moePresent.sort(),
  university_bridge: UNI_BRIDGE.filter((b) => existsBase(entries, b)).sort(),
  five_pt_denylist: prev.five_pt_denylist,
  university_denylist: prev.university_denylist,
  facet_checklists: {
    ...prev.facet_checklists,
    'equations_*': ['parametric_root_conditions', 'word_problem_setup'],
    'algebra_*': ['expression_structure', 'error_analysis'],
    'inequalities*': ['sign_chart', 'interval_notation'],
    'trigonometry_*': ['right_triangle_vs_unit_circle', 'identity_application'],
    'analytic_geometry*': ['line_circle_tangent', 'locus_reasoning'],
    'derivatives_*': ['rule_selection', 'graphical_derivative'],
    'integrals_*': ['area_interpretation', 'antiderivative_check'],
    'vectors_*': ['component_geometry', 'dot_product_meaning'],
    'kinematics_*': ['motion_graph_reading', 'vector_vs_scalar'],
    'newton_*': ['free_body_diagram', 'net_force_setup'],
    'electric_*': ['circuit_analysis_steps', 'field_vs_potential'],
    '*_makhina': ['bridge_to_uni', 'prerequisite_gaps'],
  },
  facet_evidence: {
    ...prev.facet_evidence,
    parametric_root_conditions: {
      section_keywords: ['parameter', 'for which k', 'עבור אילו', 'דיסקרימיננטה'],
      facet_tags: ['parametric_root_conditions', 'parameter_k'],
    },
    word_problem_setup: {
      section_keywords: ['word problem', 'define variables', 'בעיה מילולית', 'נגדיר'],
      facet_tags: ['word_problem_setup', 'modeling'],
    },
    expression_structure: {
      section_keywords: ['like terms', 'structure', 'מבנה הביטוי', 'איברים דומים'],
      facet_tags: ['expression_structure'],
    },
    error_analysis: {
      section_keywords: ['mistake', 'error', 'טעות', 'מצאו את השגיאה'],
      facet_tags: ['error_analysis'],
    },
    sign_chart: {
      section_keywords: ['sign chart', 'sign table', 'טבלת סימנים'],
      facet_tags: ['sign_chart'],
    },
    interval_notation: {
      section_keywords: ['interval', 'קטע', 'סימון קטעים'],
      facet_tags: ['interval_notation'],
    },
    right_triangle_vs_unit_circle: {
      section_keywords: ['right triangle', 'unit circle', 'משולש ישר', 'מעגל היחידה'],
      facet_tags: ['right_triangle_vs_unit_circle'],
    },
    identity_application: {
      section_keywords: ['identity', 'זהות', 'prove the identity'],
      facet_tags: ['identity_application'],
    },
    line_circle_tangent: {
      section_keywords: ['tangent', 'circle', 'משיק', 'מעגל'],
      facet_tags: ['line_circle_tangent'],
    },
    locus_reasoning: {
      section_keywords: ['locus', 'מקום גאומטרי'],
      facet_tags: ['locus_reasoning'],
    },
    rule_selection: {
      section_keywords: ['product rule', 'chain rule', 'באיזו נגזרת', 'כלל השרשרת'],
      facet_tags: ['rule_selection'],
    },
    graphical_derivative: {
      section_keywords: ['from the graph', 'sketch f′', 'מהגרף', 'סקיצת הנגזרת'],
      facet_tags: ['graphical_derivative'],
    },
    area_interpretation: {
      section_keywords: ['area under', 'שטח מתחת', 'definite integral'],
      facet_tags: ['area_interpretation'],
    },
    antiderivative_check: {
      section_keywords: ['differentiate to check', 'בדיקה בנגזרת', '+C'],
      facet_tags: ['antiderivative_check'],
    },
    component_geometry: {
      section_keywords: ['components', 'רכיבים', 'i hat', 'unit vector'],
      facet_tags: ['component_geometry'],
    },
    dot_product_meaning: {
      section_keywords: ['dot product', 'מכפלה סקלרית', 'projection'],
      facet_tags: ['dot_product_meaning'],
    },
    motion_graph_reading: {
      section_keywords: ['position-time', 'velocity graph', 'גרף מקום', 'גרף מהירות'],
      facet_tags: ['motion_graph_reading'],
    },
    vector_vs_scalar: {
      section_keywords: ['vector', 'scalar', 'וקטור', 'סקלר'],
      facet_tags: ['vector_vs_scalar'],
    },
    free_body_diagram: {
      section_keywords: ['free-body', 'FBD', 'דיאגרמת כוחות'],
      facet_tags: ['free_body_diagram'],
    },
    net_force_setup: {
      section_keywords: ['net force', 'ΣF', 'כוח שקול'],
      facet_tags: ['net_force_setup'],
    },
    circuit_analysis_steps: {
      section_keywords: ['Kirchhoff', 'loop', 'צומת', 'לולאה'],
      facet_tags: ['circuit_analysis_steps'],
    },
    field_vs_potential: {
      section_keywords: ['electric field', 'potential', 'שדה חשמלי', 'פוטנציאל'],
      facet_tags: ['field_vs_potential'],
    },
    bridge_to_uni: {
      section_keywords: ['university', 'Calc 1', 'מכינה', 'אוניברסיטה'],
      facet_tags: ['bridge_to_uni'],
    },
    prerequisite_gaps: {
      section_keywords: ['prerequisite', 'gap', 'פער', 'קדם'],
      facet_tags: ['prerequisite_gaps'],
    },
  },
  facet_pilot_families: [
    'functions_*',
    'sequences_*',
    'probability_*',
    'equations_*',
    'algebra_*',
    'inequalities*',
    'trigonometry_*',
    'analytic_geometry*',
    'derivatives_*',
    'integrals_*',
    'vectors_*',
    'kinematics_*',
    'newton_*',
    'electric_*',
    '*_makhina',
  ],
  matrix_basics_single_track: true,
  single_track_moe_core: true,
  single_track_physics: true,
  single_track_makhina: true,
};

fs.writeFileSync(OUT, `${JSON.stringify(contract, null, 2)}\n`);
console.log('wrote', OUT);
console.log({
  moe: contract.moe_core_concepts.length,
  req3: required_basics['3pt'].length,
  req4: required_basics['4pt'].length,
  req5: required_basics['5pt'].length,
  reqUni: required_basics.university.length,
  hsPhys: hsPhysics.length,
  uniPhys: uniPhysics.length,
  makh: makhina.length,
});
