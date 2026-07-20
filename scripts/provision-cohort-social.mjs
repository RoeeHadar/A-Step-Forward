#!/usr/bin/env node
/**
 * Provision app_users + accepted teacher links + sparse friend graph from roster.json.
 * Speeds cohort pilot (skips per-account /identity clicks). Live site still needs Clerk sign-in.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { neon } from '@neondatabase/serverless';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function loadEnvLocal() {
  const envPath = path.join(root, 'apps/web/.env.local');
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

loadEnvLocal();
const url = process.env.DATABASE_URL;
if (!url) {
  console.error('DATABASE_URL missing');
  process.exit(1);
}
const sql = neon(url);
const roster = JSON.parse(fs.readFileSync(path.join(root, 'docs/qa/cohort-pilot/roster.json'), 'utf8'));

async function upsertUser({ clerkId, role, username, realName, aboutMe }) {
  await sql`
    INSERT INTO app_users (
      clerk_user_id, role, username, real_name, nickname, about_me, profile_complete, created_at, updated_at
    )
    VALUES (
      ${clerkId}, ${role}, ${username}, ${realName}, null, ${aboutMe}, true, NOW(), NOW()
    )
    ON CONFLICT (clerk_user_id) DO UPDATE SET
      role = EXCLUDED.role,
      username = EXCLUDED.username,
      real_name = EXCLUDED.real_name,
      about_me = COALESCE(EXCLUDED.about_me, app_users.about_me),
      profile_complete = TRUE,
      updated_at = NOW()`;
}

const teacher = roster.teacher;
if (!teacher.clerk_user_id) {
  console.error('Teacher missing clerk_user_id');
  process.exit(1);
}

console.log('Upserting identities…');
await upsertUser({
  clerkId: teacher.clerk_user_id,
  role: 'educator',
  username: teacher.username_hint,
  realName: 'Pilot Teacher',
  aboutMe: 'מורה לפיילוט — מתמטיקה ופיזיקה',
});
console.log('  T1', teacher.username_hint);

for (const s of roster.students) {
  if (!s.clerk_user_id) {
    console.warn('  skip', s.id, 'no clerk id');
    continue;
  }
  await upsertUser({
    clerkId: s.clerk_user_id,
    role: 'learner',
    username: s.username_hint,
    realName: `Pilot ${s.id}`,
    aboutMe: null,
  });
  console.log(' ', s.id, s.username_hint);
}

console.log('Teacher links (accepted)…');
for (const s of roster.students) {
  if (!s.clerk_user_id) continue;
  await sql`DELETE FROM teacher_student_links WHERE student_id = ${s.clerk_user_id}`;
  await sql`
    INSERT INTO teacher_student_links (teacher_id, student_id, status, initiated_by, message, responded_at)
    VALUES (
      ${teacher.clerk_user_id}, ${s.clerk_user_id}, 'accepted', ${teacher.clerk_user_id},
      'cohort-pilot', NOW()
    )`;
  console.log('  T1 ↔', s.id);
}

const byId = Object.fromEntries(roster.students.map((s) => [s.id, s]));
const g = roster.social_graph;

async function ensureFriendship(a, b, status) {
  const A = byId[a]?.clerk_user_id;
  const B = byId[b]?.clerk_user_id;
  if (!A || !B) return;
  await sql`
    DELETE FROM friendships
    WHERE (requester_id = ${A} AND addressee_id = ${B})
       OR (requester_id = ${B} AND addressee_id = ${A})`;
  if (status === 'accepted') {
    await sql`
      INSERT INTO friendships (requester_id, addressee_id, status, responded_at)
      VALUES (${A}, ${B}, 'accepted', NOW())`;
  } else {
    await sql`
      INSERT INTO friendships (requester_id, addressee_id, status)
      VALUES (${A}, ${B}, ${status})`;
  }
}

console.log('Friend graph…');
const cluster = g.cluster ?? [];
for (let i = 0; i < cluster.length; i++) {
  for (let j = i + 1; j < cluster.length; j++) {
    await ensureFriendship(cluster[i], cluster[j], 'accepted');
    console.log('  friends', cluster[i], cluster[j]);
  }
}
if (g.pair?.length === 2) {
  await ensureFriendship(g.pair[0], g.pair[1], 'accepted');
  console.log('  friends', g.pair[0], g.pair[1]);
}
if (g.pending_from && g.pending_to) {
  await ensureFriendship(g.pending_from, g.pending_to, 'pending');
  console.log('  pending', g.pending_from, '→', g.pending_to);
}

console.log('Done.');
