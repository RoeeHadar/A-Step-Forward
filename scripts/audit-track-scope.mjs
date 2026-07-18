#!/usr/bin/env node
/**
 * audit-track-scope — track-appropriateness assist for HS math lessons.
 *
 * Catches the class of bug where a lesson's questions are gated to a points
 * level ABOVE every track the lesson serves (so NO learner ever sees them),
 * plus other track-scoping smells. This is a review ASSIST, not a hard gate:
 * true MoE syllabus scope needs human judgment (see the Q2 decision — MoE
 * questionnaires cross-checked with curriculum-categories.ts).
 *
 * Checks per lesson (subject == "math", high-school level):
 *   [E] math_track empty/invalid          -> cannot gate; toggle + planner break
 *   [E] every question gated above the top track -> hidden from ALL audiences
 *   [E] question points_level_min below the lesson's lowest track
 *   [W] a track the lesson serves has ZERO visible questions
 *   [W] lesson.math_track disagrees with kg-data points_levels (advisory)
 *
 * Usage:
 *   node scripts/audit-track-scope.mjs                 # all math lessons
 *   node scripts/audit-track-scope.mjs --only=a,b,c    # subset
 *   node scripts/audit-track-scope.mjs --json          # machine-readable
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const KG_PATH = path.join(ROOT, 'apps/web/src/lib/kg-data.json');

const LEVELS = ['3pt', '4pt', '5pt'];
const RANK = { '3pt': 0, '4pt': 1, '5pt': 2 };

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const asJson = args.get('json') === 'true';
const only = args.get('only') && args.get('only') !== 'true'
  ? new Set(args.get('only').split(',').map((s) => s.trim()))
  : null;

/** concept_id -> points_levels[] from kg-data (advisory cross-check). */
function loadKgLevels() {
  const map = new Map();
  try {
    const kg = JSON.parse(fs.readFileSync(KG_PATH, 'utf8'));
    for (const c of kg.concepts ?? []) {
      if (c.subject !== 'math') continue;
      const pts = (c.points_levels ?? []).filter((p) => LEVELS.includes(p));
      if (pts.length) map.set(c.id, pts);
    }
  } catch {
    /* advisory only */
  }
  return map;
}

function ptTracks(track) {
  return (Array.isArray(track) ? track : []).filter((t) => LEVELS.includes(t));
}

function auditLesson(lesson, kgLevels) {
  const errors = [];
  const warnings = [];
  const tracks = ptTracks(lesson.math_track);
  const questions = Array.isArray(lesson.questions) ? lesson.questions : [];

  if (tracks.length === 0) {
    const raw = Array.isArray(lesson.math_track) ? lesson.math_track : [];
    if (raw.length > 0) {
      // Non-pt track (makhina/university/calc1…) — out of the Bagrut 3/4/5pt
      // window; not gateable by points level, so skip with an advisory.
      warnings.push(`math_track ${JSON.stringify(raw)} is not a Bagrut points level — out of 3/4/5pt scope`);
    } else {
      errors.push('math_track empty — cannot gate content (toggle + planner + generator default all break)');
    }
    return { errors, warnings, visibleByTrack: {} };
  }

  const lowest = Math.min(...tracks.map((t) => RANK[t]));
  const highest = Math.max(...tracks.map((t) => RANK[t]));

  // Per-question gating sanity.
  const gatedAbove = [];
  const gatedBelow = [];
  for (const [i, q] of questions.entries()) {
    const min = q.points_level_min;
    if (!min) continue; // visible to all -> fine
    if (!LEVELS.includes(min)) {
      warnings.push(`Q${i + 1}: points_level_min '${min}' is not a valid track`);
      continue;
    }
    if (RANK[min] > highest) gatedAbove.push(i + 1);
    if (RANK[min] < lowest) gatedBelow.push(i + 1);
  }
  if (gatedAbove.length === questions.length && questions.length > 0) {
    errors.push(
      `ALL ${questions.length} questions gated above the top track (${LEVELS[highest]}) — no learner sees any question`,
    );
  } else if (gatedAbove.length > 0) {
    warnings.push(`Q[${gatedAbove.join(',')}] gated above the top track (${LEVELS[highest]}) — hidden from everyone`);
  }
  if (gatedBelow.length > 0) {
    warnings.push(`Q[${gatedBelow.join(',')}] gated below the lowest track — points_level_min under ${LEVELS[lowest]}`);
  }

  // Visible-question count per served track.
  const visibleByTrack = {};
  for (const t of tracks) {
    const r = RANK[t];
    visibleByTrack[t] = questions.filter((q) => !q.points_level_min || RANK[q.points_level_min] <= r).length;
    if (visibleByTrack[t] === 0 && questions.length > 0) {
      warnings.push(`track ${t} sees 0 of ${questions.length} questions`);
    }
  }

  // Advisory cross-check vs kg-data.
  const kg = kgLevels.get(lesson.concept_id);
  if (kg) {
    const missing = tracks.filter((t) => !kg.includes(t));
    const extra = kg.filter((t) => !tracks.includes(t));
    if (missing.length || extra.length) {
      warnings.push(
        `math_track ${JSON.stringify(tracks)} differs from kg-data ${JSON.stringify(kg)} ` +
          `(authority is curriculum-categories.ts + MoE, so verify)`,
      );
    }
  }

  return { errors, warnings, visibleByTrack };
}

function main() {
  const kgLevels = loadKgLevels();
  const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json'));
  const report = [];
  let errCount = 0;
  let warnCount = 0;

  for (const f of files) {
    const lesson = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, f), 'utf8'));
    if (lesson.subject !== 'math' || lesson.level !== 'high_school') continue;
    if (only && !only.has(lesson.concept_id)) continue;
    const { errors, warnings, visibleByTrack } = auditLesson(lesson, kgLevels);
    if (errors.length || warnings.length) {
      report.push({ concept_id: lesson.concept_id, math_track: ptTracks(lesson.math_track), errors, warnings, visibleByTrack });
      errCount += errors.length;
      warnCount += warnings.length;
    }
  }

  if (asJson) {
    console.log(JSON.stringify({ errCount, warnCount, report }, null, 2));
  } else {
    console.log('Track-scope audit — HS math lessons');
    console.log('='.repeat(60));
    for (const r of report) {
      console.log(`\n[${r.concept_id}] track=${JSON.stringify(r.math_track)} visible=${JSON.stringify(r.visibleByTrack)}`);
      for (const e of r.errors) console.log(`  ERROR  ${e}`);
      for (const w of r.warnings) console.log(`  warn   ${w}`);
    }
    console.log('\n' + '='.repeat(60));
    console.log(`Lessons flagged: ${report.length} | errors: ${errCount} | warnings: ${warnCount}`);
    console.log(errCount === 0 ? '[audit-track-scope] OK (no errors)' : '[audit-track-scope] ERRORS present');
  }
  process.exit(errCount === 0 ? 0 : 1);
}

main();
