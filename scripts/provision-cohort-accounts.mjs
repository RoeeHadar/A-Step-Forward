#!/usr/bin/env node
/**
 * provision-cohort-accounts.mjs — create Clerk users for the cohort roster.
 *
 * Requires:
 *   CLERK_SECRET_KEY in env or apps/web/.env.local
 *   --base-email you@gmail.com   (creates you+pilot_s1@gmail.com … via +alias)
 *   --password '…'               (shared pilot password; never commit)
 *
 * Usage:
 *   node scripts/provision-cohort-accounts.mjs --base-email you@gmail.com --password '…'
 *   node scripts/provision-cohort-accounts.mjs --base-email you@gmail.com --password '…' --dry-run
 *   node scripts/provision-cohort-accounts.mjs --base-email you@gmail.com --password '…' --only T1,S7
 *
 * Writes email (+ clerk id when created) back into docs/qa/cohort-pilot/roster.json
 * and docs/qa/cohort-pilot/results/credentials.local.json (gitignored pattern).
 *
 * Never commit passwords or credentials.local.json.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const rosterPath = path.join(root, 'docs/qa/cohort-pilot/roster.json');
const resultsDir = path.join(root, 'docs/qa/cohort-pilot/results');
const credPath = path.join(resultsDir, 'credentials.local.json');

function loadEnvLocal() {
  const envPath = path.join(root, 'apps/web/.env.local');
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, 'utf8').split('\n')) {
    const m = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!m) continue;
    let val = m[2].trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (!process.env[m[1]]) process.env[m[1]] = val;
  }
}

function parseArgs(argv) {
  const out = { baseEmail: null, password: null, dryRun: false, only: null };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--base-email') out.baseEmail = argv[++i];
    else if (argv[i] === '--password') out.password = argv[++i];
    else if (argv[i] === '--dry-run') out.dryRun = true;
    else if (argv[i] === '--only') {
      out.only = new Set(
        argv[++i]
          .split(',')
          .map((s) => s.trim().toUpperCase())
          .filter(Boolean),
      );
    }
  }
  return out;
}

function aliasEmail(base, slot) {
  // Clerk test emails: any address with +clerk_test verifies with OTP 424242 (no inbox).
  // Use distinct local-parts so we can have 11 accounts.
  const tag = String(slot).toLowerCase().replace(/[^a-z0-9]/g, '');
  return `asf.pilot.${tag}+clerk_test@example.com`;
}

async function clerkCreateUser({ email, password, username, firstName }) {
  const secret = process.env.CLERK_SECRET_KEY;
  if (!secret) throw new Error('CLERK_SECRET_KEY missing');
  const res = await fetch('https://api.clerk.com/v1/users', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${secret}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email_address: [email],
      password,
      username,
      first_name: firstName,
      skip_password_checks: true,
      skip_password_requirement: false,
    }),
  });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    // Already exists → look up
    if (res.status === 422 || res.status === 400) {
      const existing = await clerkFindByEmail(email);
      if (existing) return { id: existing.id, existed: true };
    }
    throw new Error(`Clerk create ${res.status}: ${text}`);
  }
  return { id: data.id, existed: false };
}

async function clerkFindByEmail(email) {
  const secret = process.env.CLERK_SECRET_KEY;
  const url = new URL('https://api.clerk.com/v1/users');
  url.searchParams.set('email_address', email);
  url.searchParams.set('limit', '10');
  const res = await fetch(url, { headers: { Authorization: `Bearer ${secret}` } });
  if (!res.ok) return null;
  const data = await res.json();
  const users = Array.isArray(data) ? data : data.data ?? [];
  return (
    users.find((u) =>
      (u.email_addresses ?? []).some(
        (e) => e.email_address?.toLowerCase() === email.toLowerCase(),
      ),
    ) ?? null
  );
}

loadEnvLocal();
const args = parseArgs(process.argv);
// --base-email is optional when using Clerk +clerk_test addresses (default).
if (!args.password) {
  console.error('Usage: --password \'…\' [--base-email ignored-for-clerk-test] [--dry-run] [--only T1,S1]');
  process.exit(1);
}
if (!args.baseEmail) args.baseEmail = 'unused@example.com';

const roster = JSON.parse(fs.readFileSync(rosterPath, 'utf8'));
const people = [
  { ...roster.teacher, kind: 'teacher' },
  ...roster.students.map((s) => ({ ...s, kind: 'student' })),
].filter((p) => !args.only || args.only.has(String(p.id).toUpperCase()));

fs.mkdirSync(resultsDir, { recursive: true });

const creds = fs.existsSync(credPath)
  ? JSON.parse(fs.readFileSync(credPath, 'utf8'))
  : { base_email: 'asf.pilot.*+clerk_test@example.com', password_set: true, accounts: {}, otp_hint: '424242' };

console.log(`Provisioning ${people.length} account(s)${args.dryRun ? ' [dry-run]' : ''}`);

for (const p of people) {
  const email = p.email || aliasEmail(args.baseEmail, p.id);
  const username = (p.username_hint || `pilot_${p.id}`).slice(0, 64);
  console.log(`\n→ ${p.id} ${email} (@${username})`);
  if (args.dryRun) continue;

  const { id, existed } = await clerkCreateUser({
    email,
    password: args.password,
    username,
    firstName: p.id,
  });
  console.log(`  ${existed ? 'exists' : 'created'} ${id}`);

  p.email = email;
  p.clerk_user_id = id;
  creds.accounts[p.id] = { email, username, clerk_user_id: id, role: p.kind };
}

if (!args.dryRun) {
  // Write roster back
  for (const p of people) {
    if (p.kind === 'teacher') {
      roster.teacher.email = p.email;
      roster.teacher.clerk_user_id = p.clerk_user_id;
    } else {
      const s = roster.students.find((x) => x.id === p.id);
      if (s) {
        s.email = p.email;
        s.clerk_user_id = p.clerk_user_id;
      }
    }
  }
  fs.writeFileSync(rosterPath, `${JSON.stringify(roster, null, 2)}\n`);
  creds.updated_at = new Date().toISOString();
  fs.writeFileSync(credPath, `${JSON.stringify(creds, null, 2)}\n`);
  console.log(`\nUpdated ${rosterPath}`);
  console.log(`Wrote ${credPath} (do not commit)`);
}

console.log('\nDone.');
