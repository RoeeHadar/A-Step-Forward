#!/usr/bin/env node
/**
 * Wave-2 cohort: provision Clerk users + identities + links + seed R1/R3.
 * Uses docs/qa/cohort-pilot/roster-w2.json (different accounts than wave 1).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { neon } from '@neondatabase/serverless';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const rosterPath = path.join(root, 'docs/qa/cohort-pilot/roster-w2.json');

function loadEnvLocal() {
  for (const raw of fs.readFileSync(path.join(root, 'apps/web/.env.local'), 'utf8').split('\n')) {
    const line = raw.replace(/\r$/, '');
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!m) continue;
    let v = m[2].trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    if (v && !process.env[m[1]]) process.env[m[1]] = v;
  }
}

loadEnvLocal();
const pw = fs.readFileSync(path.join(root, 'docs/qa/cohort-pilot/results/.pilot-password.local'), 'utf8').trim();
const roster = JSON.parse(fs.readFileSync(rosterPath, 'utf8'));

function alias(slot) {
  const tag = String(slot).toLowerCase().replace(/[^a-z0-9]/g, '');
  return `asf.w2.${tag}+clerk_test@example.com`;
}

async function createUser({ email, username, firstName }) {
  const res = await fetch('https://api.clerk.com/v1/users', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.CLERK_SECRET_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email_address: [email],
      password: pw,
      username,
      first_name: firstName,
      skip_password_checks: true,
    }),
  });
  const data = await res.json();
  if (res.ok) return { id: data.id, existed: false };
  // lookup
  const url = new URL('https://api.clerk.com/v1/users');
  url.searchParams.set('email_address', email);
  const find = await fetch(url, { headers: { Authorization: `Bearer ${process.env.CLERK_SECRET_KEY}` } });
  const list = await find.json();
  const users = Array.isArray(list) ? list : list.data ?? [];
  const match = users.find((u) =>
    (u.email_addresses ?? []).some((e) => e.email_address?.toLowerCase() === email.toLowerCase()),
  );
  if (!match?.id) throw new Error(`create failed ${res.status}: ${JSON.stringify(data)}`);
  return { id: match.id, existed: true };
}

const people = [
  { ...roster.teacher, kind: 'teacher' },
  ...roster.students.map((s) => ({ ...s, kind: 'student' })),
];

for (const p of people) {
  const email = alias(p.id);
  const username = p.username_hint;
  console.log(`→ ${p.id} ${email}`);
  const { id, existed } = await createUser({ email, username, firstName: p.id });
  console.log(`  ${existed ? 'exists' : 'created'} ${id}`);
  p.email = email;
  p.clerk_user_id = id;
  if (p.kind === 'teacher') {
    roster.teacher.email = email;
    roster.teacher.clerk_user_id = id;
  } else {
    const s = roster.students.find((x) => x.id === p.id);
    s.email = email;
    s.clerk_user_id = id;
  }
}
fs.writeFileSync(rosterPath, `${JSON.stringify(roster, null, 2)}\n`);

const sql = neon(process.env.DATABASE_URL);
async function upsertUser({ clerkId, role, username, realName }) {
  await sql`
    INSERT INTO app_users (clerk_user_id, role, username, real_name, nickname, about_me, profile_complete, created_at, updated_at)
    VALUES (${clerkId}, ${role}, ${username}, ${realName}, null, null, true, NOW(), NOW())
    ON CONFLICT (clerk_user_id) DO UPDATE SET
      role = EXCLUDED.role, username = EXCLUDED.username, real_name = EXCLUDED.real_name,
      profile_complete = TRUE, updated_at = NOW()`;
}

console.log('Identities + links…');
await upsertUser({
  clerkId: roster.teacher.clerk_user_id,
  role: 'educator',
  username: roster.teacher.username_hint,
  realName: 'Wave2 Teacher',
});
for (const s of roster.students) {
  await upsertUser({
    clerkId: s.clerk_user_id,
    role: 'learner',
    username: s.username_hint,
    realName: `Wave2 ${s.id}`,
  });
  await sql`DELETE FROM teacher_student_links WHERE student_id = ${s.clerk_user_id}`;
  await sql`
    INSERT INTO teacher_student_links (teacher_id, student_id, status, initiated_by, message, responded_at)
    VALUES (${roster.teacher.clerk_user_id}, ${s.clerk_user_id}, 'accepted', ${roster.teacher.clerk_user_id}, 'w2', NOW())`;
}

// friends R1-R3
const a = roster.students.find((s) => s.id === 'R1').clerk_user_id;
const b = roster.students.find((s) => s.id === 'R3').clerk_user_id;
await sql`DELETE FROM friendships WHERE (requester_id=${a} AND addressee_id=${b}) OR (requester_id=${b} AND addressee_id=${a})`;
await sql`INSERT INTO friendships (requester_id, addressee_id, status, responded_at) VALUES (${a}, ${b}, 'accepted', NOW())`;

console.log('Seeding R1/R3…');
for (const s of roster.students.filter((x) => x.start === 'seeded')) {
  const r = spawnSync(
    process.execPath,
    [
      path.join(root, 'scripts/seed-pilot-demo.mjs'),
      '--variant',
      s.seed_variant,
      '--goal',
      s.goal_key,
      '--user-id',
      s.clerk_user_id,
      '--anxiety',
      String(s.onboarding_anxiety),
      '--hours',
      String(s.hours_per_week_hint),
    ],
    { cwd: root, env: process.env, stdio: 'inherit' },
  );
  if (r.status !== 0) process.exit(r.status || 1);
}

console.log('Wave2 ready.');
console.log(JSON.stringify({ teacher: roster.teacher.email, students: roster.students.map((s) => ({ id: s.id, email: s.email, seed: s.seed_variant })) }, null, 2));
