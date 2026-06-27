#!/usr/bin/env node
/**
 * generate-skill-atom-questions.mjs
 *
 * For every concept in the Knowledge Graph, generates a bank of questions
 * organised by skill_atom × Bagrut level (3pt / 4pt / 5pt / hs_physics).
 *
 * Writes the result into each lesson's JSON file under "skill_atom_bank":
 *   {
 *     "<atom_name>": {
 *       "3pt": [<LessonQuestionRow>, ...],
 *       "4pt": [...],
 *       "5pt": [...]
 *     }
 *   }
 *
 * The lesson-reader and quiz-builder then draw from this bank to present
 * targeted practice on individual sub-skills.
 *
 * Usage:
 *   node scripts/generate-skill-atom-questions.mjs [--concept <id>] [--dry-run]
 *
 * Prerequisites:
 *   GROQ_API_KEY set in env
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { randomUUID } from 'crypto';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const LESSONS_DIR = path.join(__dirname, 'seed_data', 'lessons');
const KG_JSON = path.join(__dirname, '..', 'apps', 'web', 'src', 'lib', 'kg-data.json');
const GROQ_API_KEY = process.env.GROQ_API_KEY ?? '';
const GROQ_MODEL = 'llama-3.3-70b-versatile';
const DRY_RUN = process.argv.includes('--dry-run');
const QUESTIONS_PER_ATOM_LEVEL = 5; // how many questions to generate per (atom, level) pair

const CONCEPT_FILTER = (() => {
  const idx = process.argv.indexOf('--concept');
  return idx !== -1 ? process.argv[idx + 1] : null;
})();

if (!GROQ_API_KEY && !DRY_RUN) {
  console.error('GROQ_API_KEY not set.');
  process.exit(1);
}

const kg = JSON.parse(fs.readFileSync(KG_JSON, 'utf-8'));
const kgById = Object.fromEntries(kg.concepts.map(c => [c.id, c]));

const BAGRUT_DIFFICULTY_GUIDE = `
3pt questions: straightforward, numbers are small/clean, single-step or two-step reasoning.
4pt questions: multi-step, may require combining two concepts, medium-complexity algebra.
5pt questions: complex multi-step, may involve proofs or conceptual explanations, harder algebra.
hs_physics questions: context-based (word problems), applied to real-world scenarios.
`;

async function groq(messages, { maxTokens = 5000 } = {}) {
  if (DRY_RUN) return '[dry-run]';
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GROQ_API_KEY}`,
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      messages,
      temperature: 0.6, // slightly higher for question variety
      max_tokens: maxTokens,
      response_format: { type: 'json_object' },
    }),
  });
  if (!res.ok) throw new Error(`Groq error ${res.status}: ${await res.text()}`);
  const data = await res.json();
  return JSON.parse(data.choices[0].message.content);
}

/**
 * Generate questions for one (concept, skill_atom, level) triple.
 */
async function generateQuestionsForAtom(concept, atom, level, count) {
  const levelDescriptions = {
    '3pt': 'Israeli Bagrut 3-unit (beginner) level. Simple, direct, 1-2 step reasoning.',
    '4pt': 'Israeli Bagrut 4-unit (intermediate) level. Multi-step, combines concepts.',
    '5pt': 'Israeli Bagrut 5-unit (advanced) level. Complex proofs, deep reasoning.',
    'hs_physics': 'Israeli high-school physics level. Applied, word-problem style.',
  };

  const prompt = `
You are creating a question bank for the Israeli Bagrut math/physics curriculum.

Concept: ${concept.name} (${concept.id})
Concept Hebrew name: ${concept.name_he ?? concept.name}
Skill atom to target: "${atom}"
Level: ${level} — ${levelDescriptions[level]}

${BAGRUT_DIFFICULTY_GUIDE}

Generate exactly ${count} practice questions that specifically train the skill "${atom}".
Each question should be at ${level} difficulty, bilingual (English + Hebrew).

Return JSON with this schema:
{
  "questions": [
    {
      "kind": "mcq",
      "difficulty": "easy" | "medium" | "hard",
      "stem_en": "Question in English. Use $...$ for inline LaTeX, $$...$$ for block.",
      "stem_he": "Same question in Hebrew. Use $...$ for math.",
      "options_en": ["Option A", "Option B", "Option C", "Option D"],
      "options_he": ["אפשרות א", "אפשרות ב", "אפשרות ג", "אפשרות ד"],
      "correct_index": 0,
      "explanation_en": "Why this answer is correct.",
      "explanation_he": "הסבר בעברית.",
      "skill_atoms": ["${atom}"]
    }
  ]
}

Rules:
- Use a mix of question kinds: "mcq", "numeric", "short_answer", "true_false".
- For mcq/true_false: include options_en, options_he, correct_index.
- For numeric/short_answer: use correct_answer (string) instead of options.
- difficulty should match the level: 3pt → easy/medium, 5pt → medium/hard.
- Use KaTeX math formatting consistently.
- Hebrew must be natural educational Hebrew, right-to-left compatible.
- Each question must meaningfully exercise the skill atom, not just mention it.
- Vary question types and contexts across the ${count} questions.
`;

  const result = await groq([
    { role: 'system', content: 'You are an expert exam question writer. Return valid JSON only.' },
    { role: 'user', content: prompt },
  ]);

  return (result?.questions ?? []).map(q => ({
    id: randomUUID(),
    lesson_id: null, // bank questions, not tied to a specific lesson instance
    ord: 0,
    kind: q.kind ?? 'mcq',
    difficulty: q.difficulty ?? 'medium',
    stem_en: q.stem_en ?? '',
    stem_he: q.stem_he ?? '',
    options_en: q.options_en ?? null,
    options_he: q.options_he ?? null,
    correct_index: q.correct_index ?? null,
    correct_answer: q.correct_answer ?? null,
    answer_payload: null,
    rubric_en: null,
    rubric_he: null,
    explanation_en: q.explanation_en ?? '',
    explanation_he: q.explanation_he ?? '',
    skill_atoms: q.skill_atoms ?? [atom],
    points_level_min: level,
  }));
}

async function processLesson(filePath) {
  const raw = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  const conceptId = raw.concept_id;
  if (CONCEPT_FILTER && conceptId !== CONCEPT_FILTER) return;

  const kgConcept = kgById[conceptId];
  if (!kgConcept) {
    console.log(`  ⚠ No KG entry for ${conceptId}, skipping`);
    return;
  }

  const skillAtoms = kgConcept.skill_atoms ?? [];
  if (skillAtoms.length === 0) {
    console.log(`  ⚠ No skill_atoms for ${conceptId}, skipping`);
    return;
  }

  // Determine which levels are relevant
  const pointsLevels = kgConcept.points_levels ?? ['3pt'];
  const levels = pointsLevels.filter(l => ['3pt', '4pt', '5pt', 'hs_physics'].includes(l));

  if (levels.length === 0) {
    console.log(`  ⚠ No recognized levels for ${conceptId}`);
    return;
  }

  // Check if already generated
  if (raw.skill_atom_bank && Object.keys(raw.skill_atom_bank).length >= skillAtoms.length) {
    console.log(`  ✓ ${conceptId} already has skill_atom_bank, skipping`);
    return;
  }

  console.log(`  → Generating question bank for ${conceptId} (${skillAtoms.length} atoms × ${levels.length} levels)`);

  const bank = raw.skill_atom_bank ?? {};

  for (const atom of skillAtoms) {
    if (!bank[atom]) bank[atom] = {};
    for (const level of levels) {
      if (bank[atom][level] && bank[atom][level].length >= QUESTIONS_PER_ATOM_LEVEL) {
        console.log(`    ✓ ${atom}@${level} already has ${bank[atom][level].length} questions`);
        continue;
      }
      try {
        console.log(`    generating ${atom}@${level}...`);
        const questions = await generateQuestionsForAtom(kgConcept, atom, level, QUESTIONS_PER_ATOM_LEVEL);
        bank[atom][level] = questions;
        console.log(`    ✓ ${questions.length} questions`);
      } catch (err) {
        console.error(`    ✗ ${atom}@${level}: ${err.message}`);
      }
    }
  }

  const enriched = { ...raw, skill_atom_bank: bank };

  if (!DRY_RUN) {
    fs.writeFileSync(filePath, JSON.stringify(enriched, null, 2) + '\n');
    console.log(`  ✓ Saved ${conceptId}`);
  } else {
    console.log(`  [dry-run] Would save ${conceptId} with bank`);
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------
const files = fs.readdirSync(LESSONS_DIR)
  .filter(f => f.endsWith('.json'))
  .map(f => path.join(LESSONS_DIR, f));

console.log(`Processing ${files.length} lesson files`);
if (CONCEPT_FILTER) console.log(`Filtering to: ${CONCEPT_FILTER}`);
if (DRY_RUN) console.log('DRY RUN');

for (const file of files) {
  await processLesson(file);
}

console.log('\nDone!');
