#!/usr/bin/env node
/**
 * Wipe learner-bound Neon rows for a fresh start (keeps profile row by default).
 *
 * Usage:
 *   node scripts/reset-learner.mjs --email roeehadar@gmail.com
 *   node scripts/reset-learner.mjs --user-id user_xxx
 *   node scripts/reset-learner.mjs --email x@y.com --delete-profile
 *
 * Loads DATABASE_URL + CLERK_SECRET_KEY from apps/web/.env.local
 */
import fs from 'node:fs';
import path from 'node:path';
import { neon } from '@neondatabase/serverless';

function loadEnvLocal() {
  const envPath = path.join(process.cwd(), 'apps/web/.env.local');
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, 'utf8').split('\n')) {
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!m) continue;
    const key = m[1];
    let val = m[2].trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (!process.env[key]) process.env[key] = val;
  }
}

function parseArgs(argv) {
  const out = { email: null, userId: null, deleteProfile: false };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--email') out.email = argv[++i];
    else if (argv[i] === '--user-id') out.userId = argv[++i];
    else if (argv[i] === '--delete-profile') out.deleteProfile = true;
  }
  return out;
}

async function resolveUserId({ email, userId }) {
  if (userId) return userId;
  if (!email) throw new Error('Provide --email or --user-id');
  const secret = process.env.CLERK_SECRET_KEY;
  if (!secret) throw new Error('CLERK_SECRET_KEY missing in apps/web/.env.local');
  const url = new URL('https://api.clerk.com/v1/users');
  url.searchParams.set('email_address', email);
  url.searchParams.set('limit', '10');
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${secret}` },
  });
  if (!res.ok) throw new Error(`Clerk API ${res.status}: ${await res.text()}`);
  const data = await res.json();
  const users = Array.isArray(data) ? data : data.data ?? [];
  const match = users.find((u) =>
    (u.email_addresses ?? []).some((e) => e.email_address?.toLowerCase() === email.toLowerCase()),
  );
  if (!match?.id) throw new Error(`No Clerk user for ${email}`);
  return match.id;
}

loadEnvLocal();
const args = parseArgs(process.argv);
const dbUrl = process.env.DATABASE_URL;
if (!dbUrl) throw new Error('DATABASE_URL missing');

const learnerId = await resolveUserId(args);
console.log(`Resetting learner ${learnerId} …`);
const s = neon(dbUrl);

for (const [name, fn] of [
  ['chat_turns', () => s`DELETE FROM chat_turns WHERE learner_id = ${learnerId}`],
  ['learner_agent_notes', () => s`DELETE FROM learner_agent_notes WHERE learner_id = ${learnerId}`],
  ['concept_mastery', () => s`DELETE FROM concept_mastery WHERE learner_id = ${learnerId}`],
  ['skill_practice', () => s`DELETE FROM skill_practice WHERE learner_id = ${learnerId}`],
  [
    'plan_weeks',
    () =>
      s`DELETE FROM plan_weeks WHERE plan_id IN (SELECT id FROM learning_plans WHERE learner_id = ${learnerId})`,
  ],
  ['learning_plans', () => s`DELETE FROM learning_plans WHERE learner_id = ${learnerId}`],
]) {
  try {
    await fn();
    console.log(`  cleared ${name}`);
  } catch (err) {
    console.warn(`  skip ${name}:`, err instanceof Error ? err.message : err);
  }
}

if (args.deleteProfile) {
  await s`DELETE FROM learner_profiles WHERE learner_id = ${learnerId}`;
  console.log('  deleted learner_profiles');
} else {
  await s`
    UPDATE learner_profiles
    SET learner_persona = NULL,
        learner_persona_updated_at = NULL,
        wellbeing_plan_bias = NULL,
        weak_concepts = NULL,
        strong_concepts = NULL
    WHERE learner_id = ${learnerId}
  `;
  console.log('  reset persona/wellbeing on profile (profile row kept)');
}
console.log('Done.');
