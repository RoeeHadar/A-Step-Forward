#!/usr/bin/env node
/**
 * seed-cohort-pilot.mjs — seed all *seeded* students from the cohort roster.
 *
 * Reads docs/qa/cohort-pilot/roster.json. For each student with start=seeded and a
 * clerk_user_id (or email), runs seed-pilot-demo with that variant/goal/anxiety.
 *
 * Fresh students are skipped (they self-onboard). Fill email/clerk_user_id in roster
 * after Clerk signup, then:
 *
 *   $env:NODE_TLS_REJECT_UNAUTHORIZED='0'
 *   $env:DATABASE_URL='<prod Neon URL — never commit>'
 *   node scripts/seed-cohort-pilot.mjs
 *   node scripts/seed-cohort-pilot.mjs --only S7,S8
 *   node scripts/seed-cohort-pilot.mjs --dry-run
 *
 * Never commits secrets.
 */
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const rosterPath = path.join(root, 'docs/qa/cohort-pilot/roster.json');
const seedScript = path.join(root, 'scripts/seed-pilot-demo.mjs');

function loadEnvLocal() {
  const envPath = path.join(root, 'apps/web/.env.local');
  if (!fs.existsSync(envPath)) return;
  for (const raw of fs.readFileSync(envPath, 'utf8').split('\n')) {
    const line = raw.replace(/\r$/, '');
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!m) continue;
    let val = m[2].trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (val && !process.env[m[1]]) process.env[m[1]] = val;
  }
}

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const onlyIdx = args.indexOf('--only');
const only =
  onlyIdx >= 0 && args[onlyIdx + 1]
    ? new Set(
        args[onlyIdx + 1]
          .split(',')
          .map((s) => s.trim().toUpperCase())
          .filter(Boolean),
      )
    : null;

loadEnvLocal();

if (!dryRun && !process.env.DATABASE_URL && !process.env.POSTGRES_URL) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}

const roster = JSON.parse(fs.readFileSync(rosterPath, 'utf8'));
const seeded = (roster.students ?? []).filter((s) => s.start === 'seeded' && s.seed_variant);
const targets = only ? seeded.filter((s) => only.has(String(s.id).toUpperCase())) : seeded;

if (targets.length === 0) {
  console.error('No seeded students to run (check roster + --only).');
  process.exit(1);
}

console.log(`Cohort seed — ${targets.length} student(s)${dryRun ? ' [dry-run]' : ''}`);

let failed = 0;
let skipped = 0;
for (const s of targets) {
  if (!s.clerk_user_id && !s.email) {
    console.warn(`  skip ${s.id}: set clerk_user_id or email in roster.json after signup`);
    skipped += 1;
    if (dryRun) {
      console.log(
        `  (would seed) --variant ${s.seed_variant} --goal ${s.goal_key} --anxiety ${s.onboarding_anxiety} --hours ${s.hours_per_week_hint}`,
      );
    }
    continue;
  }
  const argv = [seedScript, '--variant', s.seed_variant, '--goal', s.goal_key];
  if (s.clerk_user_id) {
    argv.push('--user-id', s.clerk_user_id);
  } else {
    argv.push('--email', s.email);
  }
  if (typeof s.onboarding_anxiety === 'number') {
    argv.push('--anxiety', String(s.onboarding_anxiety));
  }
  if (typeof s.hours_per_week_hint === 'number') {
    argv.push('--hours', String(s.hours_per_week_hint));
  }

  console.log(`\n→ ${s.id} ${s.seed_variant} ${s.goal_key}`);
  if (dryRun) {
    console.log(`  node ${argv.map((a) => (/\s/.test(a) ? JSON.stringify(a) : a)).join(' ')}`);
    continue;
  }

  const r = spawnSync(process.execPath, argv, {
    cwd: root,
    env: process.env,
    stdio: 'inherit',
  });
  if (r.status !== 0) {
    failed += 1;
    console.error(`  ✗ ${s.id} failed (exit ${r.status})`);
  }
}

if (failed > 0) {
  console.error(`\nDone with ${failed} failure(s).`);
  process.exit(1);
}
if (dryRun) {
  console.log(`\nDry-run OK (${skipped} awaiting email/clerk_user_id in roster.json).`);
} else {
  console.log('\nCohort seed complete. Hard-refresh /app on each seeded account.');
}
