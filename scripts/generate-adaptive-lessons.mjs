#!/usr/bin/env node
/**
 * generate-adaptive-lessons.mjs
 *
 * Enriches every lesson JSON in scripts/seed_data/lessons/ with:
 *   1. level_focus  — per-level focus statement (3pt / 4pt / 5pt / hs_physics)
 *   2. sections[].level_min — gates advanced sections to the right level
 *   3. sections[].body_by_level — level-specific body text variants
 *   4. questions[].points_level_min — gates harder questions to the right level
 *
 * Uses Groq (llama-3.3-70b-versatile) — set GROQ_API_KEY in .env.local
 *
 * Usage:
 *   node scripts/generate-adaptive-lessons.mjs [--concept <id>] [--dry-run]
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const LESSONS_DIR = path.join(__dirname, 'seed_data', 'lessons');
const KG_JSON = path.join(__dirname, '..', 'apps', 'web', 'src', 'lib', 'kg-data.json');
const GROQ_API_KEY = process.env.GROQ_API_KEY ?? '';
const GROQ_MODEL = 'llama-3.3-70b-versatile';
const DRY_RUN = process.argv.includes('--dry-run');

const CONCEPT_FILTER = (() => {
  const idx = process.argv.indexOf('--concept');
  return idx !== -1 ? process.argv[idx + 1] : null;
})();

if (!GROQ_API_KEY && !DRY_RUN) {
  console.error('GROQ_API_KEY not set. Add it to .env.local or export it before running.');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Knowledge graph — for context
// ---------------------------------------------------------------------------
const kg = JSON.parse(fs.readFileSync(KG_JSON, 'utf-8'));
const kgById = Object.fromEntries(kg.concepts.map(c => [c.id, c]));

// ---------------------------------------------------------------------------
// Bagrut level spec — hard-coded domain knowledge so the LLM gets good context
// ---------------------------------------------------------------------------
const BAGRUT_SPEC = `
Israeli Bagrut (matriculation) math levels:
  3pt (3 units, questionnaires 801/802/803):
    - Elementary algebra, basic geometry, basic statistics & probability.
    - Parabola reading from graphs (no completing-the-square).
    - Quadratic equation: quadratic formula only (no factoring required).
    - Arithmetic/geometric sequences: terms & sums.
    - Trigonometry: basic ratios (sin/cos/tan) in right triangles; Pythagorean theorem.
    - Analytic geometry: distance, midpoint, slope; line equation y=mx+b.
    - NO derivatives, NO integrals, NO vectors, NO complex numbers.

  4pt (4 units, questionnaire 804/805):
    - All 3pt content PLUS:
    - Factoring quadratics; vertex form via completing the square.
    - Quadratic inequalities.
    - Logarithms: log laws, solving logarithmic equations.
    - Trigonometry: sine/cosine rules; unit circle; identities.
    - Analytic geometry: circles, tangent lines.
    - Sequences: recursive definitions.
    - Basic combinatorics; conditional probability; binomial distribution.

  5pt (5 units, questionnaires 581/807):
    - All 4pt content PLUS:
    - Derivatives: definition, rules, chain/product/quotient, applications.
    - Curve sketching using f' and f''.
    - Definite integrals; area between curves; improper integrals intro.
    - Differential equations (basic separation of variables).
    - Vectors; parametric equations; complex numbers (807 only).
    - Probability: Bayes theorem; distributions.

  hs_physics (high-school physics):
    - Kinematics, dynamics (Newton), energy/momentum, electricity, waves.
    - Uses basic calculus conceptually (no formal derivation required at 3-unit level).
    - Electricity: Ohm's law, circuits, magnetic fields.
    - Modern physics: photoelectric effect, nuclear models (for advanced units).
`;

// ---------------------------------------------------------------------------
// Groq caller
// ---------------------------------------------------------------------------
async function groq(messages, { temperature = 0.3, maxTokens = 4096 } = {}) {
  if (DRY_RUN) {
    return '[dry-run placeholder]';
  }
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GROQ_API_KEY}`,
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      messages,
      temperature,
      max_tokens: maxTokens,
      response_format: { type: 'json_object' },
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Groq error ${res.status}: ${text}`);
  }
  const data = await res.json();
  return JSON.parse(data.choices[0].message.content);
}

// ---------------------------------------------------------------------------
// Core: generate level_focus block for a lesson
// ---------------------------------------------------------------------------
async function generateLevelFocus(lesson, kgConcept) {
  const prompt = `
You are an Israeli Bagrut math/physics curriculum expert.
Given the lesson and knowledge graph concept below, write a "level_focus" JSON object.

${BAGRUT_SPEC}

Lesson: ${JSON.stringify({ concept_id: lesson.concept_id, title_en: lesson.title_en, summary_en: lesson.summary_en }, null, 2)}
KG concept: ${JSON.stringify(kgConcept ?? {}, null, 2)}

Return a JSON object with this exact schema — fill ONLY the levels that are relevant to this concept:
{
  "level_focus": {
    "3pt": {
      "en": "<2-3 sentences: exactly what a 3pt Bagrut student must know for this concept>",
      "he": "<same in Hebrew>",
      "bagrut_questionnaires": ["801", "802"],  // which questionnaires test this
      "skills": ["skill1", "skill2"],            // list of specific skills expected
      "not_required": ["skill_only_at_higher"]  // skills NOT needed at 3pt
    },
    "4pt": { ... same structure ... },
    "5pt": { ... same structure ... },
    "hs_physics": { ... only if relevant ... }
  }
}

Rules:
- Be precise: include actual skill names (e.g. "completing the square", "chain rule").
- "not_required" should list things students at this level should NOT be tested on.
- Only include levels that are relevant for this concept (e.g. derivatives should not have a "3pt" block).
- Hebrew text must be natural Israeli educational Hebrew.
`;

  return await groq([
    { role: 'system', content: 'You are a curriculum specialist. Return valid JSON only.' },
    { role: 'user', content: prompt },
  ]);
}

// ---------------------------------------------------------------------------
// Core: generate level_min + body_by_level for each section
// ---------------------------------------------------------------------------
async function generateSectionVariants(lesson, kgConcept) {
  const sectionsForPrompt = lesson.sections.map((s, i) => ({
    index: i,
    kind: s.kind,
    title_en: s.title_en,
    body_en_md: s.body_en_md.slice(0, 800), // truncate to save tokens
  }));

  const prompt = `
You are a Bagrut math/physics curriculum expert.
Below is a lesson and its sections. For EACH section, determine:
  1. level_min: the minimum Bagrut level needed ("3pt" | "4pt" | "5pt" | "hs_physics" | null).
     - null means the section applies to all levels.
     - "5pt" means only 5pt students need this section.
  2. body_by_level: if the section body needs to be DIFFERENT at different levels, write variants.
     Only write variants where the explanation should meaningfully differ.
     Include both "body_en_md" and "body_he_md" for each variant.
     If the section is the same at all levels, omit body_by_level.

${BAGRUT_SPEC}

Lesson: ${lesson.concept_id} — ${lesson.title_en}
Sections: ${JSON.stringify(sectionsForPrompt, null, 2)}

Return JSON with this schema:
{
  "sections": [
    {
      "index": 0,
      "level_min": null,
      "body_by_level": {
        "3pt": { "body_en_md": "...", "body_he_md": "..." },
        "5pt": { "body_en_md": "...", "body_he_md": "..." }
      }
    },
    ...
  ]
}

Rules:
- Array must have exactly ${lesson.sections.length} entries, one per section.
- For "intro" sections: level_min is usually null (everyone reads it).
- For "worked_example" sections: write 3pt variant with simple numbers, 5pt with harder.
- For theory sections gated to advanced material: set level_min = "4pt" or "5pt".
- body_by_level entries must be complete standalone explanations (don't say "see above").
- Use KaTeX for math: $...$ inline, $$...$$ block.
- Hebrew text must be right-to-left natural educational Hebrew.
- Markdown formatting is allowed (## headings, bullet lists, **bold**).
`;

  return await groq([
    { role: 'system', content: 'You are a curriculum specialist. Return valid JSON only.' },
    { role: 'user', content: prompt },
  ], { maxTokens: 6000 });
}

// ---------------------------------------------------------------------------
// Core: determine points_level_min for each question
// ---------------------------------------------------------------------------
async function generateQuestionLevels(lesson, kgConcept) {
  const questionsForPrompt = lesson.questions?.map((q, i) => ({
    index: i,
    kind: q.kind,
    difficulty: q.difficulty,
    stem_en: (q.stem_en ?? '').slice(0, 300),
    skill_atoms: q.skill_atoms ?? [],
  })) ?? [];

  if (questionsForPrompt.length === 0) return { questions: [] };

  const prompt = `
You are a Bagrut math curriculum expert.
For each question below, assign a "points_level_min" — the minimum Bagrut level at which this question would be appropriate.
Values: "3pt" | "4pt" | "5pt" | "hs_physics" | null (null = all levels).

${BAGRUT_SPEC}

Lesson concept: ${lesson.concept_id} — ${lesson.title_en}
Questions: ${JSON.stringify(questionsForPrompt, null, 2)}

Return JSON:
{
  "questions": [
    { "index": 0, "points_level_min": "3pt" },
    { "index": 1, "points_level_min": "5pt" },
    ...
  ]
}

Rules:
- Easy difficulty → usually 3pt or 4pt.
- Hard difficulty + advanced skill_atoms (derivatives, integrals, vectors) → 5pt.
- If the question tests basic recall, set null (all levels).
- Array must have exactly ${questionsForPrompt.length} entries.
`;

  return await groq([
    { role: 'system', content: 'You are a curriculum specialist. Return valid JSON only.' },
    { role: 'user', content: prompt },
  ]);
}

// ---------------------------------------------------------------------------
// Main enrichment pipeline for one lesson file
// ---------------------------------------------------------------------------
async function enrichLesson(filePath) {
  const raw = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  const conceptId = raw.concept_id;

  if (CONCEPT_FILTER && conceptId !== CONCEPT_FILTER) return;

  // Skip if already enriched (idempotent)
  if (raw.level_focus && Object.keys(raw.level_focus).length > 0) {
    const hasBodyByLevel = (raw.sections ?? []).some(s => s.body_by_level);
    const hasLevelMin = (raw.questions ?? []).some(q => q.points_level_min != null);
    if (hasBodyByLevel && hasLevelMin) {
      console.log(`  ✓ ${conceptId} already enriched, skipping`);
      return;
    }
  }

  const kgConcept = kgById[conceptId] ?? null;
  console.log(`  → Enriching ${conceptId}...`);

  try {
    // Step 1: Generate level_focus
    const focusResult = await generateLevelFocus(raw, kgConcept);
    const levelFocus = focusResult?.level_focus ?? {};

    // Step 2: Generate section variants
    const sectionResult = await generateSectionVariants(raw, kgConcept);
    const sectionUpdates = sectionResult?.sections ?? [];

    // Step 3: Generate question levels
    const questionResult = await generateQuestionLevels(raw, kgConcept);
    const questionUpdates = questionResult?.questions ?? [];

    // Merge updates back into the lesson
    const enriched = { ...raw };
    enriched.level_focus = levelFocus;

    if (enriched.sections) {
      enriched.sections = enriched.sections.map((s, i) => {
        const update = sectionUpdates.find(u => u.index === i);
        if (!update) return s;
        const merged = { ...s };
        if (update.level_min != null) merged.level_min = update.level_min;
        if (update.body_by_level && Object.keys(update.body_by_level).length > 0) {
          merged.body_by_level = update.body_by_level;
        }
        return merged;
      });
    }

    if (enriched.questions) {
      enriched.questions = enriched.questions.map((q, i) => {
        const update = questionUpdates.find(u => u.index === i);
        if (!update) return q;
        return { ...q, points_level_min: update.points_level_min ?? null };
      });
    }

    if (!DRY_RUN) {
      fs.writeFileSync(filePath, JSON.stringify(enriched, null, 2) + '\n');
      console.log(`  ✓ Saved ${conceptId}`);
    } else {
      console.log(`  [dry-run] Would save ${conceptId}`);
    }
  } catch (err) {
    console.error(`  ✗ Failed ${conceptId}:`, err.message);
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------
const files = fs.readdirSync(LESSONS_DIR)
  .filter(f => f.endsWith('.json'))
  .map(f => path.join(LESSONS_DIR, f));

console.log(`Found ${files.length} lesson files`);
if (CONCEPT_FILTER) console.log(`Filtering to concept: ${CONCEPT_FILTER}`);
if (DRY_RUN) console.log('DRY RUN — no files will be written');

for (const file of files) {
  await enrichLesson(file);
}

console.log('\nDone!');
