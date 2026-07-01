#!/usr/bin/env node
/**
 * Substantive Groq expansion — rewrite lesson sections + explanations to be
 * pedagogically deep AND fully bilingual (authentic Hebrew, not English paste).
 *
 * Usage:
 *   GROQ_API_KEY=... node scripts/expand-lessons-substantive.mjs
 *   GROQ_API_KEY=... node scripts/expand-lessons-substantive.mjs --only combinatorics,limits
 *   GROQ_API_KEY=... node scripts/expand-lessons-substantive.mjs --limit 10 --dry-run
 */
import fs from 'node:fs';
import path from 'node:path';
import { callGroq, parseJsonLoose, getGroqApiKey, sleep } from './lib/groq-client.mjs';
import {
  wordCount,
  hebrewBodyWeak,
  MIN_WORDS,
  EXPAND_SECTION_KINDS,
} from './lib/bilingual-utils.mjs';
import { normalizeLesson } from './lib/normalize-lesson.mjs';

const LESSONS_DIR = path.resolve('scripts/seed_data/lessons');
const PROGRESS_PATH = path.resolve('scripts/.expand-substantive-progress.json');

const argv = process.argv.slice(2);
function flag(name, fallback) {
  const i = argv.indexOf(`--${name}`);
  if (i < 0) return fallback;
  const v = argv[i + 1];
  if (!v || v.startsWith('--')) return true;
  return v;
}

const LIMIT = Number(flag('limit', 9999));
const ONLY = (() => {
  const raw = flag('only', null);
  if (!raw || raw === true) return null;
  return new Set(String(raw).split(',').map((s) => s.trim()).filter(Boolean));
})();
const DRY = Boolean(flag('dry-run', false));
const FORCE = Boolean(flag('force', false));
const DELAY_MS = Number(flag('delay-ms', 8000));
const SECTION_BATCH = Number(flag('section-batch', 1));
const QUESTION_BATCH = Number(flag('question-batch', 3));

const SYSTEM_PROMPT = `You are the lead bilingual curriculum author for "A Step Forward" — an AI tutoring platform for Israeli high-school (Bagrut 3/4/5 יח"ל) and first-year university students (חדו"א, אלגברה לינארית, פיזיקה).

Your job: REWRITE and EXPAND lesson section bodies so they teach clearly — like Goren/Geva / OpenStax quality, not bullet summaries.

STRICT RULES:
1. Output ONLY valid JSON. No markdown fences, no commentary.
2. Every section you return MUST have BOTH body_en_md AND body_he_md.
3. body_he_md must be FULL Hebrew prose — not a summary, not English mixed in, not transliteration-only. Math stays in $...$ / $$...$$ unchanged.
4. Use ### Move N: (EN) and ### צעד N: (HE) in worked_example sections. Name the thinking, show substitution, end with the answer.
5. intro: concrete hook + what learner will be able to do + why it matters for exams.
6. definition: each term = definition + plain-language intuition + tiny example.
7. theory: step-by-step with ### subheaders; connect ideas; avoid bare formula lists.
8. pitfall: **The mistake.** / **Why it's wrong.** / **The fix.** (and Hebrew equivalents).
9. why_matters: name related concept:<id> links where relevant + real application.
10. Do NOT use filler like "By the end of this lesson you will be able to solve standard exam problems on…" or "Why this path: We use the method from the method guide…".
11. Preserve ALL LaTeX exactly; escape backslashes for JSON (e.g. \\\\frac not broken).
12. Minimum depth (word counts are approximate — err longer):
    intro ≥110 EN / ≥90 HE; definition ≥130/110; theory ≥160/130; worked_example ≥130/110; pitfall ≥100/85; why_matters ≥90/75.
13. checkpoint_solution_*: expand to show full reasoning, not just the final number.
14. Question explanations: 80–150 words each language — why the answer works, common wrong path, exam tip.

JSON shape:
{
  "sections": [{ "index": <int>, "body_en_md": "...", "body_he_md": "..." }],
  "checkpoints": [{ "index": <int>, "checkpoint_solution_en": "...", "checkpoint_solution_he": "..." }],
  "questions": [{ "ord": <int>, "explanation_en": "...", "explanation_he": "..." }],
  "summary_en": "optional 1-2 sentence lesson summary",
  "summary_he": "optional Hebrew summary"
}`;

function loadProgress() {
  if (!fs.existsSync(PROGRESS_PATH)) return { completed: [], failed: {} };
  return JSON.parse(fs.readFileSync(PROGRESS_PATH, 'utf8'));
}

function saveProgress(progress) {
  fs.writeFileSync(PROGRESS_PATH, `${JSON.stringify(progress, null, 2)}\n`, 'utf8');
}

function sectionNeedsWork(section) {
  if (!EXPAND_SECTION_KINDS.has(section.kind)) return false;
  const min = MIN_WORDS[section.kind] ?? { en: 90, he: 75 };
  if (wordCount(section.body_en_md) < min.en) return true;
  if (hebrewBodyWeak(section.body_he_md, section.body_en_md)) return true;
  return false;
}

function lessonNeedsWork(lesson) {
  if (FORCE) return true;
  for (const s of lesson.sections ?? []) {
    if (sectionNeedsWork(s)) return true;
  }
  for (const s of lesson.sections ?? []) {
    if (s.kind === 'checkpoint') {
      if (wordCount(s.checkpoint_solution_en) < 25) return true;
      if (hebrewBodyWeak(s.checkpoint_solution_he, s.checkpoint_solution_en)) return true;
    }
  }
  for (const q of lesson.questions ?? []) {
    if (wordCount(q.explanation_en) < 55) return true;
    if (hebrewBodyWeak(q.explanation_he, q.explanation_en)) return true;
  }
  return false;
}

function trunc(text, max = 480) {
  const s = text ?? '';
  return s.length <= max ? s : `${s.slice(0, max)}…`;
}

function buildSectionPayload(lesson, sections) {
  return sections.map((s) => ({
    index: s.index,
    kind: s.kind,
    title_en: s.title_en,
    title_he: s.title_he,
    difficulty: s.difficulty,
    example_number: s.example_number,
    body_en_md: trunc(s.body_en_md),
    body_he_md: trunc(s.body_he_md),
    ...(s.kind === 'checkpoint'
      ? {
          checkpoint_solution_en: trunc(s.checkpoint_solution_en, 240),
          checkpoint_solution_he: trunc(s.checkpoint_solution_he, 240),
        }
      : {}),
  }));
}

function buildUserPrompt(lesson, sectionSlice, questionSlice) {
  const hints = lesson.agent_hints ?? {};
  const misconceptions = (hints.common_misconceptions ?? [])
    .slice(0, 3)
    .map((m) => (typeof m === 'string' ? m : `${m.wrong ?? ''} → ${m.correction ?? ''}`))
    .join('\n');

  const qSlice = questionSlice.map((q) => ({
    ord: q.ord,
    kind: q.kind,
    difficulty: q.difficulty,
    stem_en: trunc(q.stem_en, 160),
    explanation_en: trunc(q.explanation_en, 200),
    explanation_he: trunc(q.explanation_he, 200),
  }));

  return `Concept: ${lesson.concept_id}
Subject: ${lesson.subject}
Title EN: ${lesson.title_en}
Title HE: ${lesson.title_he}
Summary EN: ${lesson.summary_en ?? ''}
Summary HE: ${lesson.summary_he ?? ''}

Key insights (use in prose):
${(hints.key_insights ?? []).slice(0, 4).join('\n') || 'n/a'}

Common misconceptions (address in pitfalls / explanations):
${misconceptions || 'n/a'}

Sections to rewrite (expand deeply; keep same kind/titles; return by index):
${JSON.stringify(buildSectionPayload(lesson, sectionSlice), null, 2)}

${questionSlice.length > 0 ? `Questions — expand explanation_en and explanation_he (return by ord):\n${JSON.stringify(qSlice, null, 2)}` : ''}

Rewrite ALL listed sections/questions. Make English and Hebrew equally rich. Return JSON only.`;
}

function chunkArray(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

function mergeExpansion(lesson, parsed) {
  const out = structuredClone(lesson);

  for (const upd of parsed.sections ?? []) {
    const i = upd.index;
    if (typeof i !== 'number' || !out.sections[i]) continue;
    if (upd.body_en_md?.trim()) out.sections[i].body_en_md = upd.body_en_md.trim();
    if (upd.body_he_md?.trim()) out.sections[i].body_he_md = upd.body_he_md.trim();
    if (upd.checkpoint_solution_en?.trim()) {
      out.sections[i].checkpoint_solution_en = upd.checkpoint_solution_en.trim();
    }
    if (upd.checkpoint_solution_he?.trim()) {
      out.sections[i].checkpoint_solution_he = upd.checkpoint_solution_he.trim();
    }
  }

  for (const upd of parsed.checkpoints ?? []) {
    const i = upd.index;
    if (typeof i !== 'number' || !out.sections[i]) continue;
    if (upd.checkpoint_solution_en?.trim()) {
      out.sections[i].checkpoint_solution_en = upd.checkpoint_solution_en.trim();
    }
    if (upd.checkpoint_solution_he?.trim()) {
      out.sections[i].checkpoint_solution_he = upd.checkpoint_solution_he.trim();
    }
  }

  const qByOrd = new Map((out.questions ?? []).map((q) => [q.ord, q]));
  for (const upd of parsed.questions ?? []) {
    const q = qByOrd.get(upd.ord);
    if (!q) continue;
    if (upd.explanation_en?.trim()) q.explanation_en = upd.explanation_en.trim();
    if (upd.explanation_he?.trim()) q.explanation_he = upd.explanation_he.trim();
  }

  if (parsed.summary_en?.trim()) out.summary_en = parsed.summary_en.trim();
  if (parsed.summary_he?.trim()) out.summary_he = parsed.summary_he.trim();

  return out;
}

async function expandLesson(lesson) {
  const indexed = (lesson.sections ?? []).map((s, index) => ({ ...s, index }));
  const expandable = indexed.filter(
    (s) => EXPAND_SECTION_KINDS.has(s.kind) || s.kind === 'checkpoint',
  );

  let current = structuredClone(lesson);

  for (const batch of chunkArray(expandable, SECTION_BATCH)) {
    const userPrompt = buildUserPrompt(current, batch, []);
    const resp = await callGroq(
      [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ],
      { maxTokens: 4096, temperature: 0.4 },
    );
    if (!resp) throw new Error('Groq call failed (sections batch)');
    const parsed = parseJsonLoose(resp.content);
    current = mergeExpansion(current, parsed);
    await sleep(DELAY_MS);
  }

  const questions = current.questions ?? [];
  for (const qBatch of chunkArray(questions, QUESTION_BATCH)) {
    const userPrompt = buildUserPrompt(current, [], qBatch);
    const resp = await callGroq(
      [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ],
      { maxTokens: 4096, temperature: 0.4 },
    );
    if (!resp) throw new Error('Groq call failed (questions batch)');
    const parsed = parseJsonLoose(resp.content);
    current = mergeExpansion(current, parsed);
    await sleep(DELAY_MS);
  }

  return normalizeLesson(current);
}

async function main() {
  if (!getGroqApiKey()) {
    console.error('[expand-substantive] GROQ_API_KEY (or LLM_API_KEY) is required.');
    process.exit(2);
  }

  const progress = loadProgress();
  const completedSet = new Set(progress.completed ?? []);

  const files = fs
    .readdirSync(LESSONS_DIR)
    .filter((f) => f.endsWith('.json'))
    .sort();

  let processed = 0;
  let updated = 0;
  let skipped = 0;
  let failed = 0;

  for (const file of files) {
    if (processed >= LIMIT) break;
    const conceptId = file.replace(/\.json$/, '');
    if (ONLY && !ONLY.has(conceptId)) continue;
    if (!FORCE && completedSet.has(conceptId)) {
      skipped++;
      continue;
    }

    const fp = path.join(LESSONS_DIR, file);
    const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));

    if (!lessonNeedsWork(lesson)) {
      console.log(`[skip] ${conceptId} — already meets depth/HE gates`);
      completedSet.add(conceptId);
      skipped++;
      continue;
    }

    processed++;
    console.log(`[expand] ${conceptId} (${processed}/${LIMIT})…`);

    try {
      const expanded = await expandLesson(lesson);
      const out = `${JSON.stringify(expanded, null, 2)}\n`;
      if (!DRY) fs.writeFileSync(fp, out, 'utf8');
      completedSet.add(conceptId);
      delete progress.failed?.[conceptId];
      updated++;
      saveProgress({ ...progress, completed: [...completedSet] });
      console.log(`  ✓ ${conceptId} written`);
    } catch (err) {
      failed++;
      progress.failed = progress.failed ?? {};
      progress.failed[conceptId] = String(err.message ?? err);
      saveProgress({ ...progress, completed: [...completedSet] });
      console.error(`  ✗ ${conceptId}: ${err.message}`);
    }

    await sleep(DELAY_MS);
  }

  console.log('\n[expand-substantive] Done');
  console.log(`  updated: ${updated}, skipped: ${skipped}, failed: ${failed}, dry-run: ${DRY}`);
  if (failed > 0) process.exit(1);
}

main();
