#!/usr/bin/env node
/**
 * Audits the AI-authored lesson corpus for:
 *  - Per-lesson section count + bilingual completeness (any empty body_he?)
 *  - Per-lesson question count, grouped by kind and difficulty
 *  - Per-question bilingual completeness (stem_he/options_he/explanation_he/rubric_he)
 *  - Skill-atom usage across the corpus
 *  - agent_hints field coverage
 *
 * Run: node scripts/audit-lessons.mjs
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const DIR = 'scripts/seed_data/lessons';

const files = readdirSync(DIR).filter((f) => f.endsWith('.json')).sort();

const corpus = {
  files: 0,
  sections: 0,
  questions: 0,
  by_kind: new Map(),
  by_difficulty: new Map(),
  he_section_gaps: [],
  he_question_gaps: [],
  he_options_gaps: [],
  he_rubric_gaps: [],
  he_explanation_gaps: [],
  he_summary_gaps: [],
  questions_per_lesson: [],
  skill_atoms: new Set(),
  skill_atoms_per_lesson: new Map(),
  agent_hints_missing: [],
};

const bump = (m, k) => m.set(k, (m.get(k) ?? 0) + 1);
const isEmpty = (s) => typeof s !== 'string' || s.trim().length === 0;

for (const file of files) {
  const lesson = JSON.parse(readFileSync(join(DIR, file), 'utf8'));
  corpus.files += 1;
  if (isEmpty(lesson.summary_he)) corpus.he_summary_gaps.push(file);

  const sections = lesson.sections ?? [];
  corpus.sections += sections.length;
  sections.forEach((s, i) => {
    if (isEmpty(s.body_he_md) || isEmpty(s.title_he)) {
      corpus.he_section_gaps.push(`${file}#${i}:${s.kind}`);
    }
  });

  const questions = lesson.questions ?? [];
  corpus.questions += questions.length;
  corpus.questions_per_lesson.push({ file, n: questions.length });
  questions.forEach((q, i) => {
    bump(corpus.by_kind, q.kind ?? 'unknown');
    bump(corpus.by_difficulty, q.difficulty ?? 'unknown');
    if (isEmpty(q.stem_he)) corpus.he_question_gaps.push(`${file}#q${q.ord ?? i}`);
    if (Array.isArray(q.options_en) && (!Array.isArray(q.options_he) || q.options_en.length !== q.options_he.length)) {
      corpus.he_options_gaps.push(`${file}#q${q.ord ?? i}`);
    }
    if (q.rubric_en && isEmpty(q.rubric_he)) corpus.he_rubric_gaps.push(`${file}#q${q.ord ?? i}`);
    if (q.explanation_en && isEmpty(q.explanation_he)) corpus.he_explanation_gaps.push(`${file}#q${q.ord ?? i}`);
    for (const a of q.skill_atoms ?? []) corpus.skill_atoms.add(a);
  });

  const atoms = new Set();
  for (const q of questions) for (const a of q.skill_atoms ?? []) atoms.add(a);
  corpus.skill_atoms_per_lesson.set(file, atoms.size);

  const h = lesson.agent_hints ?? {};
  const required = ['key_insights', 'common_misconceptions', 'skill_atoms_unlocked', 'tutor_pacing_hint'];
  for (const r of required) {
    const v = h[r];
    const missing = v == null || (Array.isArray(v) ? v.length === 0 : isEmpty(v));
    if (missing) corpus.agent_hints_missing.push(`${file}::${r}`);
  }
}

console.log(`Corpus audit — ${DIR}`);
console.log('='.repeat(72));
console.log(`Files:              ${corpus.files}`);
console.log(`Sections:           ${corpus.sections}  (avg ${(corpus.sections/corpus.files).toFixed(1)}/lesson)`);
console.log(`Questions:          ${corpus.questions} (avg ${(corpus.questions/corpus.files).toFixed(1)}/lesson)`);
console.log(`Unique skill atoms: ${corpus.skill_atoms.size}`);

const fmtKey = (k) => String(k ?? 'unknown');

console.log('\nQuestions by kind:');
for (const [k, n] of [...corpus.by_kind.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${fmtKey(k).padEnd(20)} ${n}`);
}
console.log('\nQuestions by difficulty:');
for (const [k, n] of [...corpus.by_difficulty.entries()].sort((a, b) => fmtKey(a[0]).localeCompare(fmtKey(b[0])))) {
  console.log(`  ${fmtKey(k).padEnd(20)} ${n}`);
}

console.log('\nBilingual gaps (rows where HE missing while EN present):');
const reportGap = (label, arr) => {
  console.log(`  ${label.padEnd(28)} ${arr.length}`);
  if (arr.length > 0 && arr.length <= 12) {
    for (const x of arr) console.log(`      - ${x}`);
  } else if (arr.length > 12) {
    for (const x of arr.slice(0, 8)) console.log(`      - ${x}`);
    console.log(`      … (+${arr.length - 8} more)`);
  }
};
reportGap('summary_he missing', corpus.he_summary_gaps);
reportGap('section body_he_md missing', corpus.he_section_gaps);
reportGap('question stem_he missing', corpus.he_question_gaps);
reportGap('options_he mismatch/missing', corpus.he_options_gaps);
reportGap('rubric_he missing', corpus.he_rubric_gaps);
reportGap('explanation_he missing', corpus.he_explanation_gaps);

console.log('\nLessons with the FEWEST questions (top 10):');
const sortedQ = [...corpus.questions_per_lesson].sort((a, b) => a.n - b.n).slice(0, 10);
for (const { file, n } of sortedQ) console.log(`  ${n}  ${file}`);

console.log('\nLessons with the MOST questions (top 5):');
const topQ = [...corpus.questions_per_lesson].sort((a, b) => b.n - a.n).slice(0, 5);
for (const { file, n } of topQ) console.log(`  ${n}  ${file}`);

console.log('\nagent_hints field gaps:');
console.log(`  total entries missing: ${corpus.agent_hints_missing.length}`);
if (corpus.agent_hints_missing.length > 0 && corpus.agent_hints_missing.length <= 20) {
  for (const x of corpus.agent_hints_missing) console.log(`    - ${x}`);
}
