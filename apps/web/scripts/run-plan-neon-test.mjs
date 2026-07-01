import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const envPath = resolve(root, '.env.local');

try {
  const text = readFileSync(envPath, 'utf8');
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq);
    let val = trimmed.slice(eq + 1);
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (key === 'DATABASE_URL' || key === 'POSTGRES_URL' || key === 'GROQ_API_KEY') {
      process.env[key] = val;
    } else if (!process.env[key]) {
      process.env[key] = val;
    }
  }
} catch {
  // .env.local optional
}

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const valid = /^postgres(ql)?:\/\/.+@/.test(url);
console.log(`[run-plan-neon-test] DATABASE_URL valid=${valid} len=${url.length}`);

if (!valid) {
  console.warn('[run-plan-neon-test] skipping — set DATABASE_URL in apps/web/.env.local');
  process.exit(0);
}

const result = spawnSync(
  'npm',
  ['run', 'test', '--', 'src/lib/plan-neon.integration.test.ts', 'src/lib/plan-groq.integration.test.ts'],
  { cwd: root, stdio: 'inherit', env: { ...process.env, NODE_OPTIONS: '--use-system-ca' }, shell: true },
);
process.exit(result.status ?? 1);
