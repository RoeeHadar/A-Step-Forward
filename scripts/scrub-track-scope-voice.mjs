#!/usr/bin/env node
/**
 * One-shot scrub: strip Bagrut / MoE exam voice from university lessons,
 * and strip 5pt denylist phrases (ε-δ, L'Hôpital) from 5pt HS lessons.
 *
 * Usage: node scripts/scrub-track-scope-voice.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIR = path.join(ROOT, 'scripts/seed_data/lessons');

const UNI_REPLACEMENTS = [
  [/Israeli bagrut and university/gi, 'university'],
  [/bagrut and university/gi, 'university'],
  [/Bagrut 5-unit/gi, 'first-year calculus'],
  [/Bagrut 4-unit/gi, 'first-year calculus'],
  [/Bagrut 3-unit/gi, 'first-year mathematics'],
  [/5-unit Bagrut/gi, 'first-year calculus'],
  [/4-unit Bagrut/gi, 'first-year calculus'],
  [/3-unit Bagrut/gi, 'first-year mathematics'],
  [/on the Bagrut/gi, 'on university exams'],
  [/Bagrut paper/gi, 'exam paper'],
  [/Bagrut exams?/gi, 'course exam'],
  [/Bagrut math/gi, 'preparatory calculus'],
  [/\bBagrut\b/gi, 'university'],
  [/\bbagrut\b/gi, 'university'],
  [/points on the exam/gi, 'marks on the exam'],
  [/exam tip for Bagrut/gi, 'exam tip'],
  [/\b5-unit\b/gi, 'Calc-1'],
  [/\b4-unit\b/gi, 'Calc-1'],
  [/\b3-unit\b/gi, 'introductory'],
  [/\b5 units\b/gi, 'Calc 1'],
  [/\b4 units\b/gi, 'Calc 1'],
  [/\b3 units\b/gi, 'introductory courses'],
  [/\b5pt Bagrut\b/gi, 'first-year calculus'],
  [/\b4pt Bagrut\b/gi, 'first-year calculus'],
  [/\b3pt Bagrut\b/gi, 'first-year mathematics'],
  [/במבחן הבגרות/g, 'במבחן הקורס'],
  [/מבחן הבגרות/g, 'מבחן הקורס'],
  [/בחינת הבגרות/g, 'בחינת הקורס'],
  [/הבגרות/g, 'הקורס האוניברסיטאי'],
  [/בגרות/g, 'קורס אוניברסיטאי'],
  [/יחידות לימוד/g, 'קורס אוניברסיטאי'],
  [/שאלון\s*\d{3}/g, 'תרגיל קורס'],
  [/נקודות במבחן/g, 'ניקוד במבחן'],
];

/** Phrase-level scrub for 5pt leakage (keep surrounding sentence readable). */
const FIVE_PT_REPLACEMENTS = [
  [/L['']H[oô]pital['']?s?\s+rule/gi, 'algebraic limit techniques'],
  [/L['']H[oô]pital/gi, 'algebraic simplification'],
  [/לופיטל/g, 'פישוט אלגברי'],
  [/ל['']הופיטל/g, 'פישוט אלגברי'],
  [/Formal \(ε[–—-]δ\) Definition/gi, 'Informal limit idea (formal ε–δ is university)'],
  [/## Formal \(ε[–—-]δ\)[^\n]*/gi, '## Informal limit closeness (ε–δ deferred to university)'],
  [/ε[–—-]δ/g, 'limit-closeness'],
  [/\\\\varepsilon\s*[–—-]\s*\\\\delta/g, 'limit-closeness'],
  [/epsilon[-\s]*delta/gi, 'limit-closeness'],
  [/אפסילון[-\s]*דלתא/g, 'קרבה לגבול'],
  [/definition of (the )?derivative via limits/gi, 'derivative as instantaneous rate of change'],
  [/limit definition of (the )?derivative/gi, 'derivative as instantaneous rate of change'],
];

function isUniversity(lesson) {
  if (lesson.level === 'university') return true;
  const tracks = Array.isArray(lesson.math_track) ? lesson.math_track : [];
  return tracks.some((t) => ['university', 'uni', 'calc1'].includes(t));
}

function isFivePt(lesson) {
  if (isUniversity(lesson)) return false;
  const tracks = Array.isArray(lesson.math_track) ? lesson.math_track : [];
  if (tracks.includes('5pt')) return true;
  const id = String(lesson.id || '');
  return /(?:__|_)5pt$/.test(id);
}

function applyAll(text, pairs) {
  let next = text;
  for (const [re, rep] of pairs) next = next.replace(re, rep);
  return next;
}

let uni = 0;
let five = 0;
for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith('.json'))) {
  const p = path.join(DIR, f);
  const raw = fs.readFileSync(p, 'utf8');
  const lesson = JSON.parse(raw);
  let next = raw;
  if (isUniversity(lesson)) {
    const scrubbed = applyAll(next, UNI_REPLACEMENTS);
    if (scrubbed !== next) {
      next = scrubbed;
      uni++;
    }
  }
  if (isFivePt(lesson)) {
    const scrubbed = applyAll(next, FIVE_PT_REPLACEMENTS);
    if (scrubbed !== next) {
      next = scrubbed;
      five++;
    }
  }
  if (next !== raw) {
    JSON.parse(next);
    fs.writeFileSync(p, next);
    console.log('updated', f);
  }
}
console.log(`done. university-touched=${uni} five-pt-touched=${five}`);
