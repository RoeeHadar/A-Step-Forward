#!/usr/bin/env node
/*
 * Bulk question generator — Groq-backed.
 *
 * Adds N additional bilingual practice questions to each lesson JSON in
 * scripts/seed_data/lessons/ whose question count is below the target.
 * Output is written back into the same JSON files so the regular
 * `node scripts/seed-lessons.mjs` flow can pick them up on the next deploy.
 *
 * Design goals — the user's complaint was "questions are too basic and
 * cover very narrow aspects of each subject":
 *
 *   - Force MIX of kinds: mcq, mcq_multi, true_false, numeric, short_answer,
 *     match, ordering, derivation (no all-mcq files).
 *   - Force MIX of difficulties: at least one easy / medium / hard each.
 *   - Force bilingual (he + en) on every generated question.
 *   - Always derive `skill_atoms` from the lesson's `agent_hints.skill_atoms_unlocked`.
 *   - Validate every generated question against the same shape as
 *     scripts/seed-lessons.mjs and DROP any that don't pass.
 *
 * Usage:
 *
 *   GROQ_API_KEY=... node scripts/generate-bulk-questions.mjs \
 *     [--target 12]          # add questions until each lesson has ≥ target
 *     [--add N]              # cap added per lesson (default: target - current)
 *     [--limit L]            # process at most L lessons in this run
 *     [--only id1,id2]       # restrict to specific concept_ids (csv)
 *     [--dry-run]            # don't write back, just log what would be added
 *
 * Skill reference: skills/author-question-bank/SKILL.md
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const LESSONS_DIR = path.resolve(__dirname, 'seed_data', 'lessons');

// ── CLI -----------------------------------------------------------------------
const argv = process.argv.slice(2);
function flag(name, fallback) {
  const i = argv.indexOf(`--${name}`);
  if (i < 0) return fallback;
  const v = argv[i + 1];
  if (!v || v.startsWith('--')) return true;
  return v;
}
const TARGET = Number(flag('target', 12));
const ADD_OVERRIDE = flag('add', null);
const LIMIT = Number(flag('limit', 999));
const ONLY = (() => {
  const raw = flag('only', null);
  if (!raw || raw === true) return null;
  return new Set(String(raw).split(',').map((s) => s.trim()).filter(Boolean));
})();
const DRY = Boolean(flag('dry-run', false));

const GROQ_API_KEY = process.env.GROQ_API_KEY;
if (!GROQ_API_KEY) {
  console.error('[bulk-q] GROQ_API_KEY missing — set it before running.');
  process.exit(2);
}

// ── Validation (kept in sync with scripts/seed-lessons.mjs) ------------------
const Q_KINDS = new Set([
  'mcq', 'mcq_multi', 'true_false', 'open', 'short_answer',
  'fill_blank', 'numeric', 'match', 'ordering', 'derivation',
]);
const DIFFICULTIES = new Set(['easy', 'medium', 'hard']);

function isStr(x) { return typeof x === 'string' && x.trim().length > 0; }

function validateQuestion(q, ordHint) {
  if (!q || typeof q !== 'object') return 'not an object';
  if (!Q_KINDS.has(q.kind)) return `bad kind ${q.kind}`;
  if (!DIFFICULTIES.has(q.difficulty)) return `bad difficulty ${q.difficulty}`;
  for (const k of ['stem_en', 'stem_he', 'explanation_en', 'explanation_he']) {
    if (!isStr(q[k])) return `missing ${k}`;
  }
  if (!Array.isArray(q.skill_atoms)) return 'skill_atoms must be array';
  if (q.kind === 'mcq') {
    if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) return 'mcq missing options';
    if (q.options_en.length !== q.options_he.length) return 'mcq option length mismatch';
    if (typeof q.correct_index !== 'number' || q.correct_index < 0 || q.correct_index >= q.options_en.length) return 'mcq bad correct_index';
  } else if (q.kind === 'mcq_multi') {
    if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) return 'mcq_multi missing options';
    if (q.options_en.length !== q.options_he.length) return 'mcq_multi option length mismatch';
    if (!Array.isArray(q.correct_indices) || q.correct_indices.length === 0) return 'mcq_multi missing correct_indices';
    for (const idx of q.correct_indices) {
      if (typeof idx !== 'number' || idx < 0 || idx >= q.options_en.length) return 'mcq_multi out of range';
    }
  } else if (q.kind === 'true_false') {
    if (typeof q.correct_bool !== 'boolean') return 'true_false missing correct_bool';
  } else if (q.kind === 'open' || q.kind === 'derivation') {
    if (!isStr(q.rubric_en) || !isStr(q.rubric_he)) return `${q.kind} missing rubric`;
  } else if (q.kind === 'short_answer') {
    if (!Array.isArray(q.acceptable_answers) || q.acceptable_answers.length === 0) return 'short_answer needs acceptable_answers';
  } else if (q.kind === 'match') {
    for (const k of ['left_en', 'left_he', 'right_en', 'right_he']) {
      if (!Array.isArray(q[k])) return `match needs ${k}`;
    }
    if (q.left_en.length !== q.left_he.length || q.right_en.length !== q.right_he.length) return 'match length mismatch';
    if (!Array.isArray(q.correct_pairs) || q.correct_pairs.length !== q.left_en.length) return 'match correct_pairs len';
    for (const idx of q.correct_pairs) {
      if (typeof idx !== 'number' || idx < 0 || idx >= q.right_en.length) return 'match correct_pairs OOR';
    }
  } else if (q.kind === 'ordering') {
    if (!Array.isArray(q.steps_en) || !Array.isArray(q.steps_he)) return 'ordering needs steps';
    if (q.steps_en.length !== q.steps_he.length) return 'ordering length mismatch';
    if (!Array.isArray(q.correct_order) || q.correct_order.length !== q.steps_en.length) return 'ordering correct_order len';
  } else {
    // fill_blank / numeric
    if (!isStr(q.correct_answer)) return `${q.kind} needs correct_answer`;
  }
  // Force ord
  if (typeof q.ord !== 'number') q.ord = ordHint;
  return null;
}

// ── Groq call -----------------------------------------------------------------
const GROQ_MODELS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];
const GROQ_TIMEOUT_MS = 35_000;

async function callGroq(messages, { responseFormat = 'json_object' } = {}) {
  for (const model of GROQ_MODELS) {
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), GROQ_TIMEOUT_MS);
    try {
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${GROQ_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages,
          response_format: { type: responseFormat },
          max_tokens: 4096,
          temperature: 0.5,
        }),
        signal: controller.signal,
      });
      clearTimeout(t);
      if (!resp.ok) {
        console.warn(`  [groq] ${model} → ${resp.status}, falling back`);
        if (resp.status === 401 || resp.status === 403) return null;
        continue;
      }
      const body = await resp.json();
      const content = body?.choices?.[0]?.message?.content;
      if (!content) continue;
      return { content, model };
    } catch (err) {
      clearTimeout(t);
      console.warn(`  [groq] ${model} threw: ${err.message}`);
    }
  }
  return null;
}

// ── Prompt construction ------------------------------------------------------
const SYSTEM_PROMPT = `You are a senior bilingual (Hebrew + English) curriculum author for an AI tutoring platform aimed at Israeli high-school and university students.

You generate practice questions for ONE lesson at a time. STRICT requirements:

1. Output ONLY JSON, no commentary. Shape:
   { "questions": [ { ... }, { ... } ] }
2. Each question must have BOTH stem_en and stem_he, BOTH explanation_en and explanation_he, and (for kinds with options) BOTH options_en and options_he of equal length.
3. Use a MIX of question kinds. Pick freely from: mcq, mcq_multi, true_false, numeric, short_answer, match, ordering, derivation. Do not return all-mcq.
4. Use a MIX of difficulties: include at least one "easy", at least one "medium", and at least one "hard" across the batch.
5. Each question must include a "skill_atoms" array drawn ONLY from the lesson's declared skill atoms (you'll be given the list).
6. Math goes in $...$ or $$...$$ LaTeX inside both languages. Do NOT translate LaTeX.
7. Cover DIFFERENT aspects of the lesson (different sections, edge cases, common pitfalls, real-world applications). Do not duplicate the existing questions you'll be shown.
8. Per-kind shape:
   - mcq: options_en[], options_he[], correct_index (int)
   - mcq_multi: options_en[], options_he[], correct_indices (int[], length >= 1)
   - true_false: correct_bool (boolean)
   - numeric: correct_answer (string, e.g. "12.5" or "12.5 m")
   - short_answer: acceptable_answers (string[], case-insensitive variants)
   - fill_blank: correct_answer (string)
   - match: left_en[], left_he[], right_en[], right_he[] (same length), correct_pairs (int[] permutation by left index)
   - ordering: steps_en[], steps_he[], correct_order (int[] permutation of step indices)
   - open / derivation: rubric_en (string), rubric_he (string); derivation additionally may include expected_steps (string[])
9. Set "difficulty" to one of "easy", "medium", "hard".
10. Hebrew must read right-to-left (no need to flip math); use authentic mathematical Hebrew (e.g. "פתרו", "חשבו", "הוכיחו").
11. NEVER reuse the exact stem text from the existing questions list.
12. Keep each stem <= 600 chars, each explanation <= 600 chars.`;

function buildUserPrompt(lesson, addN) {
  const atoms = lesson.agent_hints?.skill_atoms_unlocked ?? [];
  const existingStems = lesson.questions.map((q, i) => `${i + 1}. [${q.kind}/${q.difficulty}] ${q.stem_en}`).join('\n');
  const sectionTitles = lesson.sections.map((s) => `- ${s.kind}: ${s.title_en}`).join('\n');
  return `Concept: ${lesson.concept_id}
Title (en): ${lesson.title_en}
Title (he): ${lesson.title_he}
Summary (en): ${lesson.summary_en}
Summary (he): ${lesson.summary_he}

Sections (use these to target different aspects):
${sectionTitles}

Allowed skill atoms (use ONLY these in each question's "skill_atoms" array):
${atoms.join(', ')}

Existing questions (DO NOT duplicate the stem text):
${existingStems}

Task: generate exactly ${addN} ADDITIONAL practice questions for this lesson, following the system rules. Make sure:
- the batch uses at least 3 different "kind" values,
- the batch contains at least one easy / medium / hard difficulty,
- every question's "skill_atoms" is a non-empty subset of the allowed list above,
- every question is fully bilingual (en + he).

Return JSON only.`;
}

// ── Lesson processing ---------------------------------------------------------
async function processLesson(file) {
  const fp = path.join(LESSONS_DIR, file);
  const raw = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  if (ONLY && !ONLY.has(raw.concept_id)) return { file, skipped: 'not in --only' };
  const currentN = Array.isArray(raw.questions) ? raw.questions.length : 0;
  const wantedTotal = Math.max(currentN, TARGET);
  const baseAdd = wantedTotal - currentN;
  const addN = ADD_OVERRIDE ? Math.min(Number(ADD_OVERRIDE), baseAdd > 0 ? baseAdd : Number(ADD_OVERRIDE)) : baseAdd;
  if (addN <= 0) return { file, skipped: `already has ${currentN} >= ${TARGET}` };

  console.log(`[bulk-q] ${file}: ${currentN} → +${addN}`);
  const result = await callGroq([
    { role: 'system', content: SYSTEM_PROMPT },
    { role: 'user', content: buildUserPrompt(raw, addN) },
  ]);
  if (!result) return { file, error: 'groq_failed' };
  let payload;
  try {
    payload = JSON.parse(result.content);
  } catch (err) {
    return { file, error: `json parse: ${err.message}` };
  }
  const generated = Array.isArray(payload?.questions) ? payload.questions : [];
  if (generated.length === 0) return { file, error: 'empty payload' };

  const allowed = new Set(raw.agent_hints?.skill_atoms_unlocked ?? []);
  const ordSeen = new Set(raw.questions.map((q) => q.ord));
  let nextOrd = Math.max(0, ...ordSeen) + 1;
  const stemSet = new Set(raw.questions.map((q) => (q.stem_en || '').trim().toLowerCase()));

  const accepted = [];
  const rejections = [];
  for (const q of generated) {
    if (typeof q !== 'object') continue;
    while (ordSeen.has(nextOrd)) nextOrd += 1;
    q.ord = nextOrd;
    if (Array.isArray(q.skill_atoms)) {
      q.skill_atoms = q.skill_atoms.filter((a) => allowed.has(a));
      if (q.skill_atoms.length === 0) q.skill_atoms = [...allowed].slice(0, 1);
    }
    const err = validateQuestion(q, nextOrd);
    if (err) {
      rejections.push({ ord: q.ord, kind: q.kind, why: err });
      continue;
    }
    const stemKey = (q.stem_en || '').trim().toLowerCase();
    if (stemSet.has(stemKey)) {
      rejections.push({ ord: q.ord, why: 'duplicate stem' });
      continue;
    }
    stemSet.add(stemKey);
    accepted.push(q);
    ordSeen.add(nextOrd);
    nextOrd += 1;
  }

  if (accepted.length === 0) {
    return { file, error: `all rejected`, rejections };
  }
  raw.questions.push(...accepted);
  if (!DRY) {
    fs.writeFileSync(fp, JSON.stringify(raw, null, 2) + '\n', 'utf-8');
  }
  return {
    file,
    added: accepted.length,
    rejected: rejections.length,
    model: result.model,
    rejections: rejections.length ? rejections : undefined,
  };
}

async function main() {
  const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
  const summary = [];
  let processed = 0;
  for (const f of files) {
    if (processed >= LIMIT) break;
    try {
      const res = await processLesson(f);
      summary.push(res);
      if (res.added) processed += 1;
    } catch (err) {
      summary.push({ file: f, error: err.message });
    }
  }
  console.log('\n[bulk-q] summary:');
  for (const r of summary) {
    if (r.skipped) console.log(`  skip ${r.file}: ${r.skipped}`);
    else if (r.error) console.log(`  ERR  ${r.file}: ${r.error}`);
    else console.log(`  ok   ${r.file}: +${r.added}${r.rejected ? ` (${r.rejected} rejected)` : ''} via ${r.model}`);
  }
  const totalAdded = summary.reduce((s, r) => s + (r.added ?? 0), 0);
  console.log(`\n[bulk-q] done: added ${totalAdded} questions across ${processed} lessons.`);
  if (DRY) console.log('[bulk-q] DRY RUN — no files were modified.');
}

main().catch((err) => {
  console.error('[bulk-q] fatal:', err);
  process.exit(1);
});
