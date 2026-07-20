#!/usr/bin/env node
/**
 * Delete previously provisioned cohort Clerk users (by clerk_user_id in roster).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
for (const raw of fs.readFileSync(path.join(root, 'apps/web/.env.local'), 'utf8').split('\n')) {
  const line = raw.replace(/\r$/, '');
  const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
  if (!m) continue;
  let v = m[2].trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
  if (v) process.env[m[1]] = v;
}

const roster = JSON.parse(fs.readFileSync(path.join(root, 'docs/qa/cohort-pilot/roster.json'), 'utf8'));
const people = [roster.teacher, ...roster.students];
const secret = process.env.CLERK_SECRET_KEY;
if (!secret) {
  console.error('CLERK_SECRET_KEY missing');
  process.exit(1);
}

for (const p of people) {
  if (!p.clerk_user_id) {
    console.log(`skip ${p.id}`);
    continue;
  }
  const res = await fetch(`https://api.clerk.com/v1/users/${p.clerk_user_id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${secret}` },
  });
  console.log(`${p.id} ${p.clerk_user_id} → ${res.status}`);
  p.clerk_user_id = null;
  p.email = null;
}
fs.writeFileSync(
  path.join(root, 'docs/qa/cohort-pilot/roster.json'),
  `${JSON.stringify(roster, null, 2)}\n`,
);
console.log('Roster cleared of clerk ids.');
