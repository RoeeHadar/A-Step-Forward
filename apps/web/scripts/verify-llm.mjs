import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
for (const line of readFileSync(resolve(root, '.env.local'), 'utf8').split(/\r?\n/)) {
  const t = line.trim();
  if (!t || t.startsWith('#')) continue;
  const i = t.indexOf('=');
  if (i <= 0) continue;
  process.env[t.slice(0, i)] = t.slice(i + 1).trim();
}

const key = process.env.LLM_API_KEY || process.env.GROQ_API_KEY;
const base = (process.env.LLM_BASE_URL || 'https://api.groq.com/openai/v1').replace(/\/+$/, '');
const model = process.env.LLM_PRIMARY_MODEL || 'llama-3.3-70b-versatile';

if (!key) {
  console.error('No LLM_API_KEY');
  process.exit(1);
}

const res = await fetch(`${base}/chat/completions`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model,
    messages: [{ role: 'user', content: 'Reply with exactly: OK' }],
    max_tokens: 10,
    temperature: 0,
  }),
});

if (!res.ok) {
  console.error('LLM verify failed', res.status, (await res.text()).slice(0, 120));
  process.exit(1);
}
const json = await res.json();
const text = json.choices?.[0]?.message?.content ?? '';
console.log('LLM verify OK — model responded:', text.trim().slice(0, 40));
