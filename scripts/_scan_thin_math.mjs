import fs from 'node:fs';
import path from 'node:path';

const dir = 'scripts/seed_data/lessons';
const genSrc = fs.readFileSync('scripts/gen/generate_math_items.py', 'utf8');
const registered = new Set(
  [...genSrc.matchAll(/["']([a-z0-9_]+)["']\s*:\s*gen_[a-z0-9_]+/g)].map((m) => m[1])
);

const rows = [];
for (const f of fs.readdirSync(dir)) {
  if (!f.endsWith('.json')) continue;
  const l = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  const subj = String(l.subject || '').toLowerCase();
  const trackRaw = Array.isArray(l.math_track) ? l.math_track.join(',') : l.math_track || '';
  const track = String(trackRaw).toLowerCase();
  const isMath =
    subj.includes('math') ||
    track.includes('pt') ||
    /math/.test((l.concept_id || '') + (l.tags || []).join(','));
  if (!isMath) continue;
  const qn = (l.questions || []).length;
  if (qn >= 15) continue;
  rows.push({
    id: l.concept_id || f.replace('.json', ''),
    qn,
    track: trackRaw || '',
    gen: registered.has(l.concept_id || f.replace('.json', '')),
    title: (l.title_en || l.title || '').slice(0, 40),
  });
}
rows.sort((a, b) => a.qn - b.qn);
console.log(`Thin math lessons (<15 q): ${rows.length}\n`);
for (const r of rows) {
  console.log(
    `${String(r.qn).padStart(2)}q  ${r.gen ? 'GEN' : '   '}  ${(r.track || '?').padEnd(6)}  ${r.id.padEnd(34)} ${r.title}`
  );
}
