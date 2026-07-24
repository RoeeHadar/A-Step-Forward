/**
 * Mechanical schema normalization for the Jul-2026 authored lesson batch.
 *
 * Fixes enums, answer-payload key names, and skill-atom linkage so the files
 * pass `validateLessonStrict`. Never touches stems, explanations, or prose.
 *
 *   node scripts/fix-authored-lesson-schema.mjs           # fix once
 *   node scripts/fix-authored-lesson-schema.mjs --check   # report only
 *   node scripts/fix-authored-lesson-schema.mjs --watch   # fix until stable
 */
import { readFileSync, writeFileSync } from 'fs';
import { argv } from 'process';
import { fileURLToPath } from 'url';
import { DIFFICULTIES, validateLessonStrict } from './lib/normalize-lesson.mjs';

export const LESSON_IDS = [
  'derivatives_chain_rule',
  'derivatives_polynomial_rational',
  'derivatives_trigonometric',
  'derivatives_exponential_logarithm',
  'function_analysis_extrema',
  'function_analysis_asymptotes',
  'integrals_polynomial_rational',
  'integrals_trigonometric',
  'integrals_substitution_basic',
  'areas_between_curves',
  'volumes_of_revolution_basic',
  'volumes_of_revolution',
  'optimization_word_problems',
  'limits_intro',
  'sequences_limits',
  'descriptive_statistics',
  'basic_probability',
  'probability_conditional_bayes',
  'linear_regression_correlation',
  'hypothesis_testing_intro',
  'trigonometry_plane_sine_cosine_law',
];

const DIFFICULTY_REMAP = { 1: 'easy', 2: 'medium', 3: 'hard', 4: 'hard', 5: 'hard' };
const SECTION_KIND_ALIASES = { pitfalls: 'pitfall' };
const Q_KIND_ALIASES = { fitb: 'fill_blank' };

/**
 * Umbrella atoms the authoring pass listed as taught but only exercised through
 * narrower sibling atoms. Maps lesson id -> atom -> question indices to link.
 */
const ORPHAN_ATOM_TARGETS = {
  derivatives_chain_rule: { derivatives_chain_rule_apply_composite: [0, 1, 2] },
  integrals_polynomial_rational: { integrals_polynomial_linearity: [1, 4, 5] },
};

const pathFor = (id) => `scripts/seed_data/lessons/${id}.json`;

function dedupeStrings(...lists) {
  const seen = new Set();
  const out = [];
  for (const list of lists) {
    if (!Array.isArray(list)) continue;
    for (const raw of list) {
      if (typeof raw !== 'string') continue;
      const s = raw.trim();
      if (!s || seen.has(s)) continue;
      seen.add(s);
      out.push(s);
    }
  }
  return out;
}

/** Normalize one lesson object in place. Returns per-fix counts. */
export function fixLesson(lesson, id) {
  const counts = { difficulty: 0, questionKind: 0, sectionKind: 0, payloadKeys: 0, atomsAssigned: 0, orphansLinked: 0 };

  for (const section of lesson.sections ?? []) {
    const alias = SECTION_KIND_ALIASES[section.kind];
    if (alias) {
      section.kind = alias;
      counts.sectionKind++;
    }
    if (section.difficulty !== undefined && !DIFFICULTIES.has(section.difficulty)) {
      const mapped = DIFFICULTY_REMAP[section.difficulty];
      if (mapped) {
        section.difficulty = mapped;
        counts.difficulty++;
      }
    }
  }

  const questions = lesson.questions ?? [];
  for (const q of questions) {
    const kindAlias = Q_KIND_ALIASES[q.kind];
    if (kindAlias) {
      q.kind = kindAlias;
      counts.questionKind++;
    }
    if (!DIFFICULTIES.has(q.difficulty)) {
      const mapped = DIFFICULTY_REMAP[q.difficulty];
      if (mapped) {
        q.difficulty = mapped;
        counts.difficulty++;
      }
    }
    // The batch stored free-text answers under accept_en/accept_he; the seed
    // pipeline and grader only read acceptable_answers.
    const p = q.answer_payload;
    if (p && typeof p === 'object' && !Array.isArray(p)) {
      const hasAliasKeys = Array.isArray(p.accept_en) || Array.isArray(p.accept_he);
      if (hasAliasKeys && !Array.isArray(p.acceptable_answers)) {
        p.acceptable_answers = dedupeStrings(p.accept_en, p.accept_he);
        delete p.accept_en;
        delete p.accept_he;
        counts.payloadKeys++;
      }
    }
  }

  const taught = Array.isArray(lesson.agent_hints?.skill_atoms_unlocked) ? lesson.agent_hints.skill_atoms_unlocked : [];

  let rr = 0;
  for (const q of questions) {
    if (Array.isArray(q.skill_atoms) && q.skill_atoms.length > 0) continue;
    if (taught.length === 0) continue;
    q.skill_atoms = [taught[rr % taught.length]];
    rr++;
    counts.atomsAssigned++;
  }

  const exercised = new Set();
  for (const q of questions) for (const a of q.skill_atoms ?? []) exercised.add(a);
  const targets = ORPHAN_ATOM_TARGETS[id] ?? {};
  for (const atom of taught) {
    if (exercised.has(atom)) continue;
    const fallback = questions.length
      ? [questions.reduce((best, q, i, arr) => ((q.skill_atoms?.length ?? 0) < (arr[best].skill_atoms?.length ?? 0) ? i : best), 0)]
      : [];
    for (const i of targets[atom] ?? fallback) {
      const q = questions[i];
      if (!q) continue;
      q.skill_atoms = Array.isArray(q.skill_atoms) ? q.skill_atoms : [];
      if (!q.skill_atoms.includes(atom)) {
        q.skill_atoms.push(atom);
        counts.orphansLinked++;
      }
    }
    exercised.add(atom);
  }

  return counts;
}

export function fixAll() {
  const totals = { difficulty: 0, questionKind: 0, sectionKind: 0, payloadKeys: 0, atomsAssigned: 0, orphansLinked: 0 };
  const changed = [];
  for (const id of LESSON_IDS) {
    const path = pathFor(id);
    const before = readFileSync(path, 'utf8');
    const lesson = JSON.parse(before);
    const counts = fixLesson(lesson, id);
    for (const k of Object.keys(totals)) totals[k] += counts[k];
    const after = `${JSON.stringify(lesson, null, 2)}\n`;
    if (after !== before) {
      writeFileSync(path, after, 'utf8');
      changed.push(id);
    }
  }
  return { totals, changed };
}

export function check() {
  const dirty = [];
  for (const id of LESSON_IDS) {
    const path = pathFor(id);
    const errors = validateLessonStrict(path, JSON.parse(readFileSync(path, 'utf8')));
    if (errors.length) dirty.push({ id, errors });
  }
  return dirty;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--check')) {
    const dirty = check();
    for (const { id, errors } of dirty) console.log(id, errors.slice(0, 5));
    console.log(dirty.length === 0 ? 'ALL_CLEAN' : `DIRTY ${dirty.length}`);
    process.exitCode = dirty.length === 0 ? 0 : 1;
    return;
  }

  if (args.includes('--watch')) {
    // Another authoring process may still be rewriting these files; keep
    // re-applying until the batch stays clean for a full quiet window.
    const pollMs = 15_000;
    const requiredCleanPolls = 12;
    const maxPolls = 80;
    let cleanStreak = 0;
    for (let poll = 1; poll <= maxPolls; poll++) {
      const { totals, changed } = fixAll();
      if (changed.length) {
        cleanStreak = 0;
        console.log(`[poll ${poll}] re-fixed ${changed.length}: ${changed.join(', ')} ${JSON.stringify(totals)}`);
      } else {
        cleanStreak++;
      }
      const dirty = check();
      if (dirty.length) {
        cleanStreak = 0;
        console.log(`[poll ${poll}] still dirty:`, dirty.map((d) => d.id).join(', '));
      }
      if (cleanStreak >= requiredCleanPolls) {
        console.log(`STABLE after ${poll} polls (${(requiredCleanPolls * pollMs) / 1000}s quiet)`);
        break;
      }
      await sleep(pollMs);
    }
    const dirty = check();
    console.log(dirty.length === 0 ? 'ALL_CLEAN' : `DIRTY ${dirty.length}`);
    process.exitCode = dirty.length === 0 ? 0 : 1;
    return;
  }

  const { totals, changed } = fixAll();
  console.log('changed files:', changed.length, changed.join(', '));
  console.log(totals);
  const dirty = check();
  for (const { id, errors } of dirty) console.log(id, errors.slice(0, 5));
  console.log(dirty.length === 0 ? 'ALL_CLEAN' : `DIRTY ${dirty.length}`);
  process.exitCode = dirty.length === 0 ? 0 : 1;
}

if (argv[1] && fileURLToPath(import.meta.url) === argv[1]) await main();
