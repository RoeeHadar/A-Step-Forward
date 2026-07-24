#!/usr/bin/env node
/**
 * Compare curriculum source-of-truth (git files) against Neon seeded projections.
 *
 * Run after `scripts/seed-lessons.mjs` in CI or locally:
 *   DATABASE_URL=... node scripts/verify-seed-drift.mjs
 *
 * Drift rules (exit 1 when violated):
 *   - lessons            — exact match (one Neon row per validated lesson JSON)
 *   - lesson_questions   — exact match (all question rows from JSON)
 *   - skill_atoms        — Neon count >= source unique atoms (seed upserts, never deletes;
 *                          extra rows are tolerated legacy atoms up to LEGACY_ATOM_TOLERANCE)
 *   - kg_edges           — Neon count >= source cross-edges (seed upserts, never deletes;
 *                          extra rows are tolerated stale edges up to LEGACY_EDGE_TOLERANCE)
 *
 * Env: DATABASE_URL or POSTGRES_URL (same as seed-lessons.mjs).
 */
import fs from 'node:fs';
import path from 'node:path';
import { neon } from '@neondatabase/serverless';
import { normalizeLesson, validateLesson } from './lib/normalize-lesson.mjs';

const LESSONS_DIR = 'scripts/seed_data/lessons';
const CROSS_EDGES_PATH = 'apps/web/src/lib/kg-cross-edges.json';

/** Max extra skill_atoms rows in Neon vs source (legacy atoms not yet purged). */
const LEGACY_ATOM_TOLERANCE = 100;
/** Max extra kg_edges rows in Neon vs source (removed edges not yet purged). */
const LEGACY_EDGE_TOLERANCE = 20;

function countSourceOfTruth() {
  if (!fs.existsSync(LESSONS_DIR)) {
    console.error(`lessons dir not found: ${LESSONS_DIR}`);
    process.exit(1);
  }

  const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
  const atoms = new Set();
  let questionCount = 0;
  let validLessons = 0;
  const validationErrors = [];

  for (const file of files) {
    const fp = path.join(LESSONS_DIR, file);
    let raw;
    try {
      raw = JSON.parse(fs.readFileSync(fp, 'utf-8'));
    } catch (e) {
      validationErrors.push({ file, error: `JSON parse: ${e.message}` });
      continue;
    }
    const data = normalizeLesson(raw, file);
    const errs = validateLesson(file, data);
    if (errs.length) {
      validationErrors.push({ file, error: errs.join('; ') });
      continue;
    }
    validLessons += 1;
    questionCount += data.questions.length;
    for (const atom of data.agent_hints?.skill_atoms_unlocked ?? []) atoms.add(atom);
    for (const q of data.questions) {
      for (const atom of q.skill_atoms ?? []) atoms.add(atom);
    }
  }

  if (validationErrors.length) {
    console.error(`[verify-seed-drift] ${validationErrors.length} invalid lesson file(s):`);
    for (const { file, error } of validationErrors.slice(0, 10)) {
      console.error(`  ${file}: ${error}`);
    }
    process.exit(2);
  }

  let edgeCount = 0;
  if (fs.existsSync(CROSS_EDGES_PATH)) {
    const crossEdges = JSON.parse(fs.readFileSync(CROSS_EDGES_PATH, 'utf-8'));
    edgeCount = (crossEdges.edges ?? []).filter((e) => e.src && e.dst && e.relation).length;
  }

  return {
    lessons: validLessons,
    lesson_questions: questionCount,
    skill_atoms: atoms.size,
    kg_edges: edgeCount,
  };
}

async function countNeon(sql) {
  const [lessonsRow] = await sql`SELECT COUNT(*)::int AS n FROM lessons`;
  const [questionsRow] = await sql`SELECT COUNT(*)::int AS n FROM lesson_questions`;
  const [atomsRow] = await sql`SELECT COUNT(*)::int AS n FROM skill_atoms`;
  const [edgesRow] = await sql`SELECT COUNT(*)::int AS n FROM kg_edges`;

  return {
    lessons: lessonsRow.n,
    lesson_questions: questionsRow.n,
    skill_atoms: atomsRow.n,
    kg_edges: edgesRow.n,
  };
}

function checkMetric(name, source, neon, rule) {
  const ok = rule(source, neon);
  const delta = neon - source;
  const deltaStr = delta === 0 ? '0' : delta > 0 ? `+${delta}` : String(delta);
  return { name, source, neon, delta: deltaStr, ok, rule: rule.label };
}

const RULES = {
  lessons: Object.assign(
    (source, neon) => neon === source,
    { label: 'exact match' },
  ),
  lesson_questions: Object.assign(
    (source, neon) => neon === source,
    { label: 'exact match' },
  ),
  skill_atoms: Object.assign(
    (source, neon) => neon >= source && neon <= source + LEGACY_ATOM_TOLERANCE,
    { label: `>= source, <= source + ${LEGACY_ATOM_TOLERANCE} legacy` },
  ),
  kg_edges: Object.assign(
    (source, neon) => neon >= source && neon <= source + LEGACY_EDGE_TOLERANCE,
    { label: `>= source, <= source + ${LEGACY_EDGE_TOLERANCE} legacy` },
  ),
};

async function main() {
  const source = countSourceOfTruth();
  console.log('[verify-seed-drift] Source of truth:', source);

  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
  if (!url) {
    console.error('DATABASE_URL must be set');
    process.exit(1);
  }

  const sql = neon(url);
  const neonCounts = await countNeon(sql);
  console.log('[verify-seed-drift] Neon:', neonCounts);

  const rows = Object.keys(RULES).map((key) =>
    checkMetric(key, source[key], neonCounts[key], RULES[key]),
  );

  const col = (s, w) => String(s).padEnd(w);
  const wName = 18;
  const wNum = 10;
  console.log('');
  console.log(
    `${col('metric', wName)} ${col('source', wNum)} ${col('neon', wNum)} ${col('delta', 8)} rule`,
  );
  console.log('-'.repeat(72));
  for (const r of rows) {
    const status = r.ok ? 'OK' : 'FAIL';
    console.log(
      `${col(r.name, wName)} ${col(r.source, wNum)} ${col(r.neon, wNum)} ${col(r.delta, 8)} ${r.rule} [${status}]`,
    );
  }

  const failed = rows.filter((r) => !r.ok);
  if (failed.length) {
    console.error(`\n[verify-seed-drift] ${failed.length} metric(s) out of tolerance`);
    process.exit(1);
  }

  console.log('\n[verify-seed-drift] All metrics within tolerance');
}

main().catch((err) => {
  console.error('[verify-seed-drift] fatal:', err);
  process.exit(1);
});
