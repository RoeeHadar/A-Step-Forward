#!/usr/bin/env node
/**
 * Print a one-time Clerk sign-in URL for a cohort persona (T1, S1…).
 * Usage: node scripts/cohort-signin-url.mjs T1
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
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

loadEnvLocal();
const id = (process.argv[2] || '').toUpperCase();
const roster = JSON.parse(fs.readFileSync(path.join(root, 'docs/qa/cohort-pilot/roster.json'), 'utf8'));
const person =
  id === 'T1'
    ? roster.teacher
    : roster.students.find((s) => String(s.id).toUpperCase() === id);
if (!person?.clerk_user_id) {
  console.error('Unknown persona or missing clerk_user_id:', id);
  process.exit(1);
}
const secret = process.env.CLERK_SECRET_KEY;
if (!secret) {
  console.error('CLERK_SECRET_KEY missing');
  process.exit(1);
}

const res = await fetch('https://api.clerk.com/v1/sign_in_tokens', {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${secret}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ user_id: person.clerk_user_id, expires_in_seconds: 3600 }),
});
const data = await res.json();
if (!res.ok) {
  console.error(data);
  process.exit(1);
}
console.log(data.url || data.token);
