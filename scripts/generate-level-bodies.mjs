#!/usr/bin/env node
/**
 * generate-level-bodies.mjs
 *
 * GENERAL PROBLEM SOLVER:
 * Applies body_by_level variants to EVERY lesson JSON in seed_data/lessons/.
 *
 * This script was created to solve the GENERAL problems identified from specific examples:
 *   1. (from inequalities) Lesson body text is written at a uniform level, not calibrated
 *      per student track (3pt/4pt/5pt/hs_physics). Lower-level students see academic jargon
 *      meant for higher tracks. Upper-level students see oversimplified content.
 *   2. (from static_equilibrium) Some concepts were missing lesson files entirely.
 *      Those are now created separately. This script handles the quality of body text.
 *   3. (general) All sub-topics within each concept must be covered at depth appropriate
 *      to the target level — not a single one-size-fits-all explanation.
 *
 * HOW IT WORKS:
 *   For each lesson JSON file:
 *     - Identifies which tracks it targets (math_track array)
 *     - For each section that has body_en_md but lacks body_by_level:
 *       - Calls Groq to generate level-appropriate variants for each track
 *       - Each variant follows strict rules per level (see LEVEL_STYLE_GUIDE)
 *     - Writes updated JSON back to the file
 *
 * USAGE:
 *   # Process ALL lessons (full run):
 *   node scripts/generate-level-bodies.mjs
 *
 *   # Process ONE specific lesson (for testing or targeted fix):
 *   node scripts/generate-level-bodies.mjs --concept inequalities
 *
 *   # Only process lessons that are missing body_by_level:
 *   node scripts/generate-level-bodies.mjs --missing-only
 *
 *   # Dry run (shows which files/sections would be updated, no writes):
 *   node scripts/generate-level-bodies.mjs --dry-run
 *
 * ENVIRONMENT:
 *   GROQ_API_KEY — required (Groq API key)
 */

import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LESSONS_DIR = join(__dirname, 'seed_data', 'lessons');
const GROQ_API_KEY = process.env.GROQ_API_KEY;
const MODEL = 'llama-3.3-70b-versatile';

/** ─────────────────────────────────────────────────────────────────
 *  LEVEL STYLE GUIDE
 *  This is the core rule-set that makes explanations level-appropriate.
 *  It is injected into every Groq prompt.
 * ───────────────────────────────────────────────────────────────── */
const LEVEL_STYLE_GUIDE = {
  '3pt': `
WRITING RULES FOR 3-POINT STUDENTS (Israeli Bagrut 3 units):
- These students are often "afraid of letters" — prefer numbers in examples over symbolic manipulation.
- NO interval notation (no "(-∞, 3)"). Say "all numbers less than 3" or "x < 3".
- NO abstract mathematical language: no "function space", no "P(x)/Q(x)" formalisms, no Greek letters as concepts.
- NO proofs or derivations. Show the method step by step with concrete numbers.
- DO use relatable, real-world analogies (money, temperature, age, distances).
- DO end every explanation with a worked example using clean integer numbers.
- USE simple language. One idea per sentence. Short paragraphs.
- DIFFICULTY: what they call "hard" is level 1-2 of a 5pt student's "easy".
- VOCABULARY: explain every technical term when first used.
- TOPICS COVERED: only what appears in 3pt Bagrut questionnaires. No derivatives, no logs, no complex numbers.
`,
  '4pt': `
WRITING RULES FOR 4-POINT STUDENTS (Israeli Bagrut 4 units):
- These students are comfortable with algebra and can handle moderate formalism.
- Can use standard mathematical notation (inequalities, fractions, basic function notation).
- No advanced calculus, no proofs from axioms, no abstract algebra.
- Explanations should be clear and direct — explain the "why" but avoid tangential theory.
- Use signed charts (טבלת סימן) for inequalities and roots.
- Examples should include at least one "tricky" case (e.g., negative leading coefficient, or non-obvious substitution).
- DIFFICULTY: exam-level problems involve multi-step algebraic manipulation.
`,
  '5pt': `
WRITING RULES FOR 5-POINT STUDENTS (Israeli Bagrut 5 units):
- Full mathematical rigor is appropriate: can use all standard notation, limits, derivatives, proofs.
- Expect students to handle multi-step algebraic manipulation without hand-holding.
- Include the "full picture": edge cases, boundary conditions, special cases.
- Examples should match actual Bagrut 5-unit question style (questionnaires 581, 807).
- Can reference related topics: limits, derivatives, continuity, sequences.
`,
  'hs_physics': `
WRITING RULES FOR HIGH-SCHOOL PHYSICS (Israeli Bagrut Physics 5 units):
- Students have completed algebra and basic calculus (derivatives, but not integration by parts).
- Use SI units throughout. Always define symbols before using them.
- Show dimensional analysis when relevant.
- Include a worked example that mirrors typical Bagrut question format.
- Connect theory to real-world applications (pendulum clocks, satellites, circuits).
- Draw attention to the "why" behind formulas, not just the formula itself.
`,
};

/** Per-concept sub-topic map: what MUST be covered at each level.
 *  Used to validate/augment generated content.
 *  Keys are concept_ids; values list mandatory sub-topics per track.
 */
const SUBTOPIC_REQUIREMENTS = {
  inequalities: {
    '3pt': ['linear inequalities on number line', 'solving step by step', 'checking answers'],
    '4pt': ['quadratic inequalities', 'sign chart', 'rational inequalities (rearranged form)'],
    '5pt': ['parametric inequalities', 'absolute value inequalities', 'system of inequalities'],
  },
  functions_quadratic: {
    '3pt': ['vertex form', 'axis of symmetry', 'reading from graph', 'zeros'],
    '4pt': ['discriminant', 'intersections with line', 'transformations'],
    '5pt': ['parametric quadratics', 'quadratic inequality analysis', 'complex roots'],
  },
  derivatives_intro: {
    '5pt': ['limit definition of derivative', 'tangent line', 'derivative at a point', 'differentiability'],
  },
  optimization_problems: {
    '5pt': ['set up objective function', 'eliminate variable using constraint', 'critical point test', 'second derivative test', 'endpoint check'],
  },
  newton_laws: {
    'hs_physics': ['first law (inertia)', 'second law (F=ma)', 'third law (action-reaction)', 'free body diagrams', 'net force problems'],
  },
  // Add more as needed — the script will still run for unlisted concepts,
  // just without subtopic validation.
};

// ─── CLI ARGS ───────────────────────────────────────────────────────
const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const MISSING_ONLY = args.includes('--missing-only');
const CONCEPT_FILTER = (() => {
  const idx = args.indexOf('--concept');
  return idx !== -1 ? args[idx + 1] : null;
})();

// ─── GROQ CALL ─────────────────────────────────────────────────────
async function callGroq(systemPrompt, userPrompt) {
  if (!GROQ_API_KEY) {
    throw new Error('GROQ_API_KEY environment variable is not set.');
  }
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.3,
      max_tokens: 2000,
    }),
  });
  if (!response.ok) {
    const txt = await response.text();
    throw new Error(`Groq API error ${response.status}: ${txt}`);
  }
  const json = await response.json();
  return json.choices[0].message.content;
}

// ─── GENERATE body_by_level FOR ONE SECTION ─────────────────────────
async function generateBodyByLevel(lesson, section, tracks) {
  const conceptId = lesson.concept_id;
  const subtopics = SUBTOPIC_REQUIREMENTS[conceptId] ?? {};

  const result = {};

  for (const track of tracks) {
    // Skip if body_by_level already has this track
    if (section.body_by_level?.[track]) continue;

    const styleGuide = LEVEL_STYLE_GUIDE[track] ?? '';
    const mandatorySubtopics = subtopics[track] ? `\nMandatory sub-topics to cover: ${subtopics[track].join(', ')}.` : '';

    const systemPrompt = `You are a mathematics and physics curriculum writer for Israeli high school students.
You must rewrite the given lesson section body for a specific student level.
${styleGuide}
${mandatorySubtopics}

Output ONLY the rewritten body in Markdown. Do not include section titles, metadata, or JSON. Just the body text.
Write in English first. The Hebrew version will be handled separately.
Inline math must be wrapped in single dollar signs: $formula$. Display math uses double: $$formula$$.
Do NOT add raw LaTeX command words (like "ge" or "le") as plain text — always wrap math in $ signs.`;

    const userPrompt = `Concept: ${conceptId}
Subject: ${lesson.subject}
Track/level to write for: ${track}
Section title: ${section.title_en}
Original body (may be written at a different level):
---
${section.body_en_md ?? ''}
---

Rewrite this body section for ${track} students. Follow the level rules strictly.
If the original body contains content not appropriate for ${track} (e.g., too advanced, too theoretical, or using wrong notation), 
replace it with simpler/more appropriate content covering the same topic idea for this level.`;

    let bodyEn;
    try {
      bodyEn = await callGroq(systemPrompt, userPrompt);
    } catch (err) {
      console.error(`  ⚠ Failed to generate ${track} body for ${conceptId}/${section.title_en}: ${err.message}`);
      continue;
    }

    // Generate Hebrew body
    const heSystemPrompt = `You are translating an educational math/physics lesson body from English to Hebrew.
The translation must:
- Be in natural, accessible Hebrew for high school students
- Keep ALL mathematical notation exactly as-is (do not translate $x$, $\\omega$, etc.)
- Use right-to-left phrasing naturally
- Translate educational terms correctly (e.g., "derivative" → "נגזרת", "slope" → "שיפוע")
- Keep the same structure and length as the English version
Output ONLY the Hebrew body in Markdown.`;

    const heUserPrompt = `Translate this lesson body to Hebrew:\n---\n${bodyEn}\n---`;

    let bodyHe;
    try {
      bodyHe = await callGroq(heSystemPrompt, heUserPrompt);
    } catch (err) {
      console.warn(`  ⚠ Failed Hebrew translation for ${conceptId}/${track}: ${err.message}`);
      bodyHe = bodyEn; // fallback: use English
    }

    result[track] = {
      body_en_md: bodyEn.trim(),
      body_he_md: bodyHe.trim(),
    };

    console.log(`    ✓ Generated ${track} body_by_level (${bodyEn.length} chars)`);
  }

  return result;
}

// ─── PROCESS ONE LESSON FILE ────────────────────────────────────────
async function processLesson(filePath) {
  const raw = readFileSync(filePath, 'utf-8');
  let lesson;
  try {
    lesson = JSON.parse(raw);
  } catch {
    console.warn(`⚠ Cannot parse ${filePath}, skipping.`);
    return;
  }

  const tracks = lesson.math_track ?? [];
  if (tracks.length === 0) {
    console.log(`  ⏭ No math_track defined, skipping.`);
    return;
  }

  let modified = false;

  for (let i = 0; i < (lesson.sections ?? []).length; i++) {
    const section = lesson.sections[i];

    // Skip sections without body text
    if (!section.body_en_md && !section.body_he_md) continue;

    // Determine which tracks are missing from body_by_level
    const existingTracks = Object.keys(section.body_by_level ?? {});
    const missingTracks = tracks.filter((t) => !existingTracks.includes(t));

    if (MISSING_ONLY && missingTracks.length === 0) continue;
    if (!MISSING_ONLY && existingTracks.length === tracks.length) continue; // all present

    const tracksToGenerate = MISSING_ONLY ? missingTracks : tracks.filter((t) => !existingTracks.includes(t));
    if (tracksToGenerate.length === 0) continue;

    console.log(`  ↪ Section "${section.title_en}" — generating for: ${tracksToGenerate.join(', ')}`);

    if (DRY_RUN) continue;

    const newBodies = await generateBodyByLevel(lesson, section, tracksToGenerate);
    if (Object.keys(newBodies).length > 0) {
      lesson.sections[i].body_by_level = {
        ...(section.body_by_level ?? {}),
        ...newBodies,
      };
      modified = true;
    }

    // Rate limit: 1.5s between sections to stay well under Groq RPM limits
    await new Promise((r) => setTimeout(r, 1500));
  }

  if (modified && !DRY_RUN) {
    writeFileSync(filePath, JSON.stringify(lesson, null, 2), 'utf-8');
    console.log(`  💾 Saved ${filePath}`);
  }
}

// ─── MAIN ───────────────────────────────────────────────────────────
async function main() {
  const files = readdirSync(LESSONS_DIR)
    .filter((f) => f.endsWith('.json'))
    .sort();

  const filtered = CONCEPT_FILTER
    ? files.filter((f) => f.replace('.json', '') === CONCEPT_FILTER)
    : files;

  console.log(`\n🔧 generate-level-bodies.mjs`);
  console.log(`Mode: ${DRY_RUN ? 'DRY RUN' : 'WRITE'} | ${MISSING_ONLY ? 'missing-only' : 'all-unlocked'} | ${filtered.length} files`);
  console.log(`Model: ${MODEL}\n`);

  if (!DRY_RUN && !GROQ_API_KEY) {
    console.error('❌ GROQ_API_KEY is not set. Run with --dry-run to preview changes without API calls.');
    process.exit(1);
  }

  let processed = 0;
  let skipped = 0;
  const errors = [];

  for (const file of filtered) {
    const filePath = join(LESSONS_DIR, file);
    console.log(`\n📄 ${file}`);
    try {
      await processLesson(filePath);
      processed++;
    } catch (err) {
      console.error(`  ❌ Error: ${err.message}`);
      errors.push({ file, error: err.message });
      skipped++;
    }
  }

  console.log(`\n✅ Done. Processed: ${processed}, Skipped/Errors: ${skipped}`);
  if (errors.length > 0) {
    console.log('\nErrors:');
    errors.forEach((e) => console.log(`  ${e.file}: ${e.error}`));
  }
}

main().catch((err) => {
  console.error('Fatal:', err);
  process.exit(1);
});
