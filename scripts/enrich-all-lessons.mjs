#!/usr/bin/env node
// ⚠ Corporate proxy / self-signed CA: bypass TLS verification
// This is safe for outbound API calls to well-known services (Groq).
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

/**
 * enrich-all-lessons.mjs
 *
 * THE COMPREHENSIVE LESSON ENRICHER
 * ==================================
 * Generates body_by_level for ALL sections of ALL lesson JSON files,
 * targeting each lesson's math_track tracks.
 *
 * One Groq call per lesson → generates ALL sections × ALL tracks in JSON.
 * This is 10× faster than calling per-section and produces better results
 * because the model has full context of the entire lesson.
 *
 * USAGE:
 *   GROQ_API_KEY=... node scripts/enrich-all-lessons.mjs
 *   GROQ_API_KEY=... node scripts/enrich-all-lessons.mjs --concept inequalities
 *   GROQ_API_KEY=... node scripts/enrich-all-lessons.mjs --force   # overwrites existing
 *
 * OUTPUT: Updates JSON files in-place. Run seed-lessons.mjs afterwards to push to DB.
 */

import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LESSONS_DIR = join(__dirname, 'seed_data', 'lessons');
const GROQ_API_KEY = process.env.GROQ_API_KEY;
// llama-3.1-8b-instant: 500k tokens/day free tier (vs 100k for 70b) — use for bulk enrichment
// Switch back to llama-3.3-70b-versatile for quality passes on individual lessons
const MODEL = process.env.GROQ_MODEL ?? 'llama-3.1-8b-instant';
const args = process.argv.slice(2);
const FORCE = args.includes('--force');
const CONCEPT_FILTER = (() => {
  const i = args.indexOf('--concept');
  return i !== -1 ? args[i + 1] : null;
})();

// ─── LEVEL STYLE GUIDE ────────────────────────────────────────────
const LEVEL_RULES = {
  '3pt': `3-POINT BAGRUT RULES (most important level — highest student count):
• Students are concrete thinkers who prefer numbers over symbols
• NO: interval notation (-∞,3), no P(x)/Q(x) notation, no "open/closed sets", no proofs
• NO: jargon like "domain of a function" without immediately explaining with example
• YES: "let's take a concrete number and check" approach
• YES: step-by-step with plain-language labels for each step
• YES: real-world analogies (money, age, temperature, distance)
• YES: "the trick is..." and "watch out for..." language
• Difficulty calibration: 3pt "hard" = 4pt "easy". Keep it accessible.
• Every section ends with at least one fully worked numeric example
• Max 2 new concepts per section`,

  '4pt': `4-POINT BAGRUT RULES:
• Students are comfortable with algebra and formal notation
• CAN use: sign charts (טבלת סימן), function notation, rational expressions
• Should explain "why" behind each method, not just "how"
• Include the "tricky case" in examples (e.g., quadratic with negative leading coefficient)
• Examples should build from straightforward to exam-level within the section
• Difficulty calibration: 4pt exam questions involve 3-4 algebraic steps
• Connect to prerequisite concepts when helpful`,

  '5pt': `5-POINT BAGRUT RULES:
• Full mathematical rigor. Students are comfortable with limits, derivatives, proofs.
• Include complete derivations when they deepen understanding
• Edge cases and boundary conditions must be addressed
• Examples should match Bagrut questionnaires 581 / 807 difficulty
• Can reference connections to calculus, complex numbers, linear algebra where relevant
• "Hard" means multi-step problems requiring insight, not just computation`,

  'hs_physics': `HIGH SCHOOL PHYSICS (Bagrut Physics 5 units) RULES:
• Always define every symbol before using it in a formula
• Show units in all calculations, e.g., F = 10 kg × 2 m/s² = 20 N
• Include a real-world example or application (bridge, satellite, circuit, etc.)
• Connect to kinematics/Newton laws where applicable
• Worked examples must show: given → find → formula → substitute → answer
• "Hard" means multi-step problems requiring application of 2+ concepts simultaneously
• Every formula should be accompanied by a sentence explaining what each term means`,
};

// ─── COMPREHENSIVE SUBTOPIC REQUIREMENTS PER CONCEPT ─────────────
// This ensures completeness — no sub-topic is left out.
const REQUIRED_SUBTOPICS = {
  // ── MATH 3pt ──
  arithmetic: { '3pt': ['integers', 'fractions', 'decimals', 'order of operations (PEMDAS)', 'negative numbers', 'absolute value', 'rounding'] },
  algebra_basics: { '3pt': ['variable definition', 'like terms', 'distributive property', 'evaluating expressions', 'translating words to algebra'] },
  equations_linear: { '3pt': ['solving with one variable', 'moving terms across equals', 'equations with fractions', 'equations with parentheses', 'word problems to equations'] },
  equations_quadratic: { '3pt': ['factoring method', 'quadratic formula', 'discriminant', 'word problems'], '5pt': ['Vieta formulas', 'parametric quadratics', 'complex roots'] },
  inequalities: { '3pt': ['linear on number line', 'solving step by step', 'double inequalities'], '4pt': ['quadratic inequality', 'sign chart', 'rational inequalities after rearranging'], '5pt': ['absolute value inequalities', 'parametric inequalities'] },
  exponents: { '3pt': ['positive integer exponents', 'zero and negative exponents', 'exponent rules: product/quotient/power', 'scientific notation'] },
  word_problems: { '3pt': ['percentages (all 3 types)', 'age problems', 'distance-speed-time', 'mixture problems', 'rate problems'] },
  functions_intro: { '3pt': ['domain and range', 'function notation f(x)', 'vertical line test', 'table of values', 'increasing vs decreasing'] },
  functions_linear: { '3pt': ['slope-intercept form', 'calculating slope', 'x-intercept and y-intercept', 'parallel and perpendicular', 'graphing'] },
  functions_quadratic: { '3pt': ['parabola shape', 'vertex', 'axis of symmetry', 'zeros', 'graphing from equation'], '4pt': ['discriminant and intersections', 'transformations of parabola'], '5pt': ['parametric quadratics', 'quadratic inequality analysis'] },
  sequences_arithmetic: { '4pt': ['general term formula', 'sum of n terms', 'finding a₁ and d from two terms', 'word problems'] },
  analytic_geometry_basic: { '3pt': ['distance formula', 'midpoint formula', 'slope', 'line equation y=mx+b', 'parallel/perpendicular lines', 'intersection of two lines'] },
  geometry_basics: { '3pt': ['angles: complementary/supplementary/vertical', 'triangle angle sum', 'Pythagorean theorem', 'area and perimeter formulas', 'similar triangles', 'basic circle: area and circumference'] },
  trigonometry_ratios: { '3pt': ['sin/cos/tan definitions in right triangle', 'finding unknown sides', 'finding unknown angles', '30-45-60 special angles', 'word problems with heights/distances'], '4pt': ['sine rule', 'cosine rule', '3D trigonometry'] },
  descriptive_stats: { '3pt': ['mean', 'median', 'mode', 'range', 'reading bar/pie/line charts', 'frequency tables'], '4pt': ['standard deviation', 'quartiles', 'box plots', 'normal distribution intro'] },
  probability_basic: { '3pt': ['probability as fraction', 'complementary events', 'AND vs OR', 'tree diagrams'], '4pt': ['conditional probability', 'Bayes theorem intro', 'binomial distribution'] },
  // ── MATH 4pt ──
  fractions_algebraic: { '4pt': ['simplifying rational expressions', 'multiplying/dividing', 'adding/subtracting with common denominator', 'domain restrictions'] },
  factoring: { '4pt': ['common factor', 'difference of squares', 'trinomial factoring', 'grouping', 'sum/difference of cubes'] },
  functions_exponential: { '4pt': ['exponential growth and decay', 'graphing', 'compound interest connection', 'natural base e intro'] },
  sequences_geometric: { '4pt': ['general term', 'sum of n terms', 'compound interest application'], '5pt': ['infinite geometric series', 'convergence condition', 'recurring decimals'] },
  quadrilaterals: { '4pt': ['parallelogram: 4 sufficient conditions', 'rhombus properties', 'rectangle properties', 'trapezoid midline', 'proof techniques'] },
  triangles_congruence: { '3pt': ['SSS, SAS, ASA, AAS criteria', 'proving triangles congruent', 'using congruence to prove side/angle equal'] },
  circles: { '4pt': ['chord properties', 'tangent line', 'inscribed angle theorem', 'arc length and sector area', 'circle equation (x-a)²+(y-b)²=r²'] },
  combinatorics: { '4pt': ['permutations (ordered)', 'combinations (unordered)', 'Pascal triangle', 'binomial theorem', 'counting with restrictions'] },
  // ── MATH 5pt ──
  logarithms: { '4pt': ['log definition and basic properties', 'log rules: product/quotient/power', 'change of base'], '5pt': ['natural log ln', 'solving log equations', 'log inequalities', 'exponential equations via log'] },
  function_transformations: { '5pt': ['vertical shift', 'horizontal shift (counterintuitive!)', 'reflection over x and y axes', 'vertical stretch/compress', 'composition of transformations', 'domain and range after transformation'] },
  trigonometry_identities: { '4pt': ['Pythagorean identity', 'double angle formulas', 'compound angle formulas'], '5pt': ['proving identities', 'half-angle formulas', 'product-to-sum formulas'] },
  trigonometry_equations: { '4pt': ['solving sin/cos/tan = k', 'general solution', 'equations reducible to quadratic'], '5pt': ['equations with identities', 'parametric trigonometric equations'] },
  analytic_geometry: { '4pt': ['circle equation', 'intersection of line and circle'], '5pt': ['ellipse', 'parabola (conic)', 'hyperbola', 'conic sections general form', 'tangent lines to conics'] },
  vectors_2d: { '5pt': ['vector addition/subtraction', 'scalar multiplication', 'dot product', 'angle between vectors', 'unit vector', 'vector proof of geometric theorems'] },
  distributions: { '5pt': ['normal distribution', 'standard score (z-score)', 'binomial distribution', 'Poisson distribution', 'expectation and variance'] },
  limits: { '5pt': ['limit definition', 'limit laws', 'limits at infinity', 'indeterminate forms (0/0, ∞/∞)', "L'Hôpital's rule intro", 'continuity and limits'] },
  derivatives_intro: { '5pt': ['limit definition of derivative', 'tangent line interpretation', 'differentiability', 'derivative at a point', 'notation: f′, dy/dx'] },
  derivatives_rules: { '5pt': ['constant, power rule', 'sum/difference', 'product rule', 'quotient rule', 'chain rule', 'implicit differentiation intro'] },
  derivatives_applications: { '5pt': ['increasing/decreasing', 'critical points', 'local max/min', 'second derivative test', 'concavity and inflection', 'sketching curves'] },
  optimization_problems: { '5pt': ['setup objective function', 'eliminate variable via constraint', 'critical points', 'second derivative test', 'endpoint check', 'fence/box/cylinder problems'] },
  integrals_intro: { '5pt': ['antiderivative concept', 'indefinite integral', 'power rule for integrals', 'constant of integration', 'simple integration rules'] },
  definite_integrals: { '5pt': ['Riemann sum idea', 'Fundamental Theorem of Calculus', 'area under curve', 'signed area', 'properties of definite integrals'] },
  integrals_techniques: { '5pt': ['substitution (u-sub)', 'integration by parts', 'trigonometric integrals', 'partial fractions intro'] },
  integrals_applications: { '5pt': ['area between curves', 'volume of revolution', 'average value', 'arc length intro'] },
  complex_numbers: { '5pt': ['standard form a+bi', 'arithmetic operations', 'modulus and argument', 'polar form', 'De Moivre theorem', 'roots of unity'] },
  continuity: { '5pt': ['continuity definition', 'types of discontinuity', 'Intermediate Value Theorem', 'continuity of compositions'] },
  hypothesis_testing: { '5pt': ['null and alternative hypothesis', 't-test', 'p-value', 'Type I and Type II errors', 'confidence intervals'] },
  differential_equations_intro: { '5pt': ['order and degree', 'separable equations', 'initial value problems', 'exponential growth/decay models'] },
  // ── PHYSICS ──
  units_measurement: { 'hs_physics': ['SI units', 'dimensional analysis', 'significant figures', 'scientific notation', 'unit conversion', 'measurement uncertainty'] },
  vectors_basics: { 'hs_physics': ['vector vs scalar', 'components (x,y)', 'vector addition (tip-to-tail and component)', 'unit vectors', 'dot product'] },
  kinematics_1d: { 'hs_physics': ['displacement vs distance', 'velocity vs speed', 'acceleration', 'constant acceleration equations (4 kinematic equations)', 'free fall', 'v-t and x-t graphs'] },
  kinematics_2d: { 'hs_physics': ['2D position vector', 'velocity components', 'relative motion', 'frame of reference'] },
  projectile_motion: { 'hs_physics': ['horizontal: constant velocity', 'vertical: free fall', 'time of flight', 'maximum height', 'range formula', 'launch angle optimization'] },
  newton_laws: { 'hs_physics': ['First law: inertia', 'Second law: F=ma', 'Third law: action-reaction pairs', 'free body diagrams', 'net force problems', 'elevator problems', 'Atwood machine'] },
  friction: { 'hs_physics': ['static vs kinetic friction', 'coefficient of friction', 'friction on inclined plane', 'friction in circular motion'] },
  circular_motion: { 'hs_physics': ['centripetal acceleration a=v²/r', 'centripetal force', 'banking curves', 'vertical circles', 'period and frequency'] },
  gravitation: { 'hs_physics': ["Newton's law of universal gravitation", 'g on planet surface', 'g at altitude', 'orbital motion', 'orbital speed and period', "Kepler's third law", 'weightlessness'] },
  work_energy: { 'hs_physics': ['work W=Fd·cosθ', 'kinetic energy KE=½mv²', 'work-energy theorem', 'power P=W/t', 'potential energy (gravitational and spring)', 'energy conservation'] },
  conservation_energy: { 'hs_physics': ['conservation of mechanical energy', 'with/without friction', 'spring potential energy', 'roller coaster problems', 'collision energy changes'] },
  momentum: { 'hs_physics': ['impulse J=FΔt', 'conservation of momentum', 'elastic vs inelastic collisions', 'center of mass motion', 'rocket propulsion'] },
  collisions: { 'hs_physics': ['elastic: both KE and p conserved', 'perfectly inelastic: objects stick', 'coefficient of restitution', '2D collisions'] },
  simple_harmonic_motion: { 'hs_physics': ['restoring force', 'period of spring T=2π√(m/k)', 'period of pendulum T=2π√(L/g)', 'displacement, velocity, acceleration in SHM', 'energy in SHM', 'resonance'] },
  torque: { 'hs_physics': ['torque τ=rF·sinθ', 'moment arm', 'rotational equilibrium', 'center of mass and gravity', 'pivot point choice'] },
  static_equilibrium: { 'hs_physics': ['ΣF=0 (translational)', 'Στ=0 (rotational)', 'pivot point strategy', 'beam problems', 'ladder problems'] },
  rotational_kinematics: { 'hs_physics': ['angular displacement (radians)', 'angular velocity ω', 'angular acceleration α', '4 rotational kinematic equations', 'v=rω, a_t=rα', 'rpm to rad/s conversion'] },
  rotational_dynamics: { 'hs_physics': ['moment of inertia I', 'τ=Iα', 'rotational kinetic energy ½Iω²', 'rolling without slipping', 'angular momentum L=Iω'] },
  waves_basics: { 'hs_physics': ['transverse vs longitudinal', 'wavelength λ, frequency f, period T', 'wave speed v=fλ', 'interference (constructive/destructive)', 'reflection and transmission', 'standing waves'] },
  sound_waves: { 'hs_physics': ['longitudinal wave', 'speed of sound in air', 'intensity and decibels', 'pitch and frequency', 'harmonics in pipes'] },
  doppler: { 'hs_physics': ['Doppler effect for sound', 'approaching source: higher f', 'receding: lower f', 'formula with source and observer motion', 'red/blue shift in light'] },
  optics_geometric: { 'hs_physics': ['reflection: law of reflection', 'refraction: Snell\'s law', 'total internal reflection', 'converging/diverging lenses', 'thin lens equation 1/f=1/d_o+1/d_i', 'magnification'] },
  optics_physical: { 'hs_physics': ['wave nature of light', 'double-slit interference', 'diffraction', 'Young\'s experiment: path difference condition', 'diffraction grating'] },
  electrostatics: { 'hs_physics': ["Coulomb's law", 'electric force', 'superposition principle', 'charge distribution', 'conductors vs insulators'] },
  electric_field: { 'hs_physics': ['E field definition E=F/q', 'field lines', 'uniform field between plates', 'point charge field', 'E and force relationship', 'motion of charge in E field'] },
  electric_potential: { 'hs_physics': ['potential V=kQ/r', 'potential difference (voltage)', 'work done W=qΔV', 'equipotential surfaces', 'capacitance C=Q/V'] },
  electric_circuits: { 'hs_physics': ['Ohm\'s law V=IR', 'series vs parallel', 'equivalent resistance', 'power P=IV=I²R', 'EMF and internal resistance', 'measuring V and I'] },
  kirchhoff_laws: { 'hs_physics': ['KCL: current at junction', 'KVL: voltage around loop', 'multi-loop circuits', 'Wheatstone bridge'] },
  magnetism: { 'hs_physics': ['magnetic force F=qv×B', 'right-hand rule', 'force on current: F=BIL', 'magnetic field of straight wire', 'solenoid field', 'mass spectrometer'] },
  electromagnetic_induction: { 'hs_physics': ["Faraday's law", 'magnetic flux Φ=BAcosθ', "Lenz's law", 'induced EMF in moving conductor', 'generator principle', 'transformer'] },
  ac_circuits: { 'hs_physics': ['AC vs DC', 'peak and RMS values', 'resistor, capacitor, inductor in AC', 'impedance', 'resonance', 'power factor'] },
  modern_physics_intro: { 'hs_physics': ['blackbody radiation', 'photoelectric effect', 'photon energy E=hf', 'de Broglie wavelength', 'Heisenberg uncertainty principle'] },
  atomic_models: { 'hs_physics': ['Thomson model', 'Rutherford model', 'Bohr model', 'energy levels', 'emission/absorption spectra', 'quantum numbers intro'] },
  nuclear_physics: { 'hs_physics': ['nuclear notation (A, Z, N)', 'binding energy', 'radioactive decay: α, β, γ', 'half-life', 'nuclear fission and fusion', 'mass-energy E=mc²'] },
  special_relativity: { 'hs_physics': ['postulates of SR', 'time dilation Δt=γΔt₀', 'length contraction L=L₀/γ', 'Lorentz factor γ', 'mass-energy equivalence', 'relativistic momentum'] },
  angular_momentum: { 'hs_physics': ['L=Iω or L=mvr', 'conservation of angular momentum', 'spinning skater effect', 'gyroscope precession', 'torque and L change'] },
};

// ─── GROQ CALL ────────────────────────────────────────────────────
// NOTE: We do NOT use response_format: json_object because Groq's JSON mode
// fails (json_validate_failed) when the output exceeds ~3k tokens. Instead we
// ask for JSON in the prompt and extract it with a regex from the response.
async function callGroq(systemPrompt, userPrompt, retries = 4) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: { Authorization: `Bearer ${GROQ_API_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: MODEL,
          messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userPrompt }],
          temperature: 0.25,
          max_tokens: 500,
          // 500 max_tokens: ~700 total tokens/call → safely fits 8 calls/min in 6k TPM window
          // One section at a time → no truncation possible
        }),
      });
      if (response.status === 429) {
        // Exponential back-off: 30s, 60s, 90s, 120s …
        const wait = Math.min((attempt + 1) * 30000, 120000);
        console.log(`  ⏳ Rate limited (attempt ${attempt + 1}/${retries}), waiting ${wait / 1000}s...`);
        lastErr = new Error('Rate limited after all retries');
        await new Promise((r) => setTimeout(r, wait));
        continue;
      }
      if (!response.ok) {
        const txt = await response.text();
        throw new Error(`HTTP ${response.status}: ${txt.slice(0, 200)}`);
      }
      const json = await response.json();
      return json.choices[0].message.content ?? '';
    } catch (err) {
      lastErr = err;
      if (attempt === retries) throw err;
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  throw lastErr ?? new Error('callGroq exhausted retries');
}

// Compact level hint for system prompt
const LEVEL_HINT = {
  '3pt': 'Basic 3-pt Bagrut: concrete numbers, no jargon, simple examples, no proofs.',
  '4pt': '4-pt Bagrut: formal algebra OK, explain "why", sign charts, exam-level examples.',
  '5pt': '5-pt Bagrut: full rigor, complete derivations, edge cases, proof techniques.',
  'hs_physics': 'HS Physics Bagrut: define every symbol, show units, worked given→find→formula→answer.',
};

// ─── ENRICH ONE SECTION × ONE TRACK per API call ─────────────────────────
// This is the ONLY approach that works within Groq's 6k TPM limit:
//   ~300 tokens input + ~400 tokens output = ~700 tokens/call
//   → safe at 10-second intervals (4200 tokens/min < 6000 TPM)
//
// Output format: plain text with ===EN=== / ===HE=== delimiters.
// No JSON = no truncation errors.
async function enrichOneSection(lesson, section, track) {
  const subtopics = REQUIRED_SUBTOPICS[lesson.concept_id] ?? {};
  const topics = (subtopics[track] ?? []).slice(0, 4).join(', ');

  const systemPrompt = `You are an Israeli curriculum writer. ALL math in LaTeX: $inline$, $$display$$.
Level: ${LEVEL_HINT[track] ?? track}
Write 3-5 sentences + 1 worked numeric example. Be direct and concise.
Output ONLY:
===EN===
[English content]
===HE===
[Hebrew translation]`;

  const userPrompt = `Lesson: ${lesson.title_en} | Section: ${section.title_en} | Level: ${track}${topics ? `\nCover: ${topics}` : ''}`;

  let raw;
  try {
    raw = await callGroq(systemPrompt, userPrompt);
  } catch (err) {
    throw err;
  }

  if (!raw) return null;

  const enMatch = raw.match(/===EN===\s*([\s\S]*?)(?====HE===|$)/);
  const heMatch = raw.match(/===HE===\s*([\s\S]*?)$/);

  const en = enMatch?.[1]?.trim();
  const he = heMatch?.[1]?.trim();

  if (!en) return null;
  return { body_en_md: en, body_he_md: he ?? en };
}

// ─── ENRICH ONE LESSON (loops sections × tracks) ─────────────────────────
async function enrichLesson(lesson) {
  const tracks = lesson.math_track ?? [];
  if (tracks.length === 0) return false;

  const subtopics = REQUIRED_SUBTOPICS[lesson.concept_id] ?? {};
  let anyModified = false;
  let callsMade = 0;

  for (const track of tracks) {
    const sectionsNeedingTrack = (lesson.sections ?? []).filter((s) => {
      if (!s.body_en_md && !s.body_he_md) return false;
      if (FORCE) return true;
      return !s.body_by_level?.[track];
    });

    if (sectionsNeedingTrack.length === 0) {
      process.stdout.write(`  ⏭ ${track}: all sections present\n`);
      continue;
    }

    let trackSaved = 0;
    for (const section of sectionsNeedingTrack) {
      // Inter-call delay: 10s → 6 calls/min → 700 tok/call → 4200 tok/min < 6k TPM
      if (callsMade > 0) await new Promise((r) => setTimeout(r, 10000));
      callsMade++;

      try {
        const result = await enrichOneSection(lesson, section, track);
        if (!result) { process.stdout.write(`    ⚠ no content for "${section.title_en}"\n`); continue; }

        const idx = lesson.sections.indexOf(section);
        lesson.sections[idx].body_by_level = lesson.sections[idx].body_by_level ?? {};
        lesson.sections[idx].body_by_level[track] = result;
        anyModified = true;
        trackSaved++;
      } catch (err) {
        process.stdout.write(`    ❌ [${track}] "${section.title_en}": ${err.message.slice(0, 80)}\n`);
      }
    }
    if (trackSaved > 0) process.stdout.write(`  ✔ ${track}: ${trackSaved}/${sectionsNeedingTrack.length} sections saved\n`);
  }

  return anyModified;
}

// ─── MAIN ────────────────────────────────────────────────────────
async function main() {
  if (!GROQ_API_KEY) {
    console.error('❌ GROQ_API_KEY not set.');
    process.exit(1);
  }

  const files = readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
  const filtered = CONCEPT_FILTER ? files.filter((f) => f.replace('.json', '') === CONCEPT_FILTER) : files;

  console.log(`\n🚀 enrich-all-lessons.mjs — ${filtered.length} files | force=${FORCE}`);
  console.log(`Model: ${MODEL}\n`);

  let processed = 0, enriched = 0, errors = 0;

  for (const file of filtered) {
    const fp = join(LESSONS_DIR, file);
    const raw = JSON.parse(readFileSync(fp, 'utf-8'));
    console.log(`\n[${processed + 1}/${filtered.length}] ${raw.concept_id} (${(raw.math_track ?? []).join('+')})`);

    try {
      const changed = await enrichLesson(raw);
      if (changed) {
        writeFileSync(fp, JSON.stringify(raw, null, 2), 'utf-8');
        console.log(`  ✅ Saved enriched ${raw.concept_id}`);
        enriched++;
      } else {
        console.log(`  ⏭ Already complete`);
      }
    } catch (err) {
      console.error(`  ❌ Fatal: ${err.message}`);
      errors++;
    }

    processed++;
    // No extra inter-lesson pause — the per-section 10s delay already throttles correctly
  }

  console.log(`\n✅ Done. Files: ${processed} | Enriched: ${enriched} | Errors: ${errors}`);
  console.log('\nNext step: cd apps/web && node ../../scripts/seed-lessons.mjs');
}

main().catch((err) => { console.error('Fatal:', err); process.exit(1); });
