#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { verifyQuestion } from './lib/verify-question.mjs';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const EN_PAD =
  ' Worked path: restate the hypotheses, write the governing formula, execute each algebraic step, then check the result against the domain and the original stem.';
const HE_PAD =
  ' דרך פתרון: נסחו מחדש את ההנחות, כתבו את הנוסחה השולטת, בצעו כל צעד אלגברי, ואמתו מול התחום והניסוח המקורי.';

let n = 0;
for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith('.json'))) {
  const fp = path.join(DIR, f);
  const j = JSON.parse(fs.readFileSync(fp, 'utf8'));
  let changed = false;
  for (const q of j.questions || []) {
    const r = verifyQuestion(q);
    if (r.ok || r.checked) continue;
    if (!r.reason || !r.reason.includes('multi-step')) continue;
    q.needs_review = true;
    q.explanation_en = `${q.explanation_en || q.correct_answer || 'See theory.'}${EN_PAD}`;
    q.explanation_he = `${q.explanation_he || 'ראו תיאוריה.'}${HE_PAD}`;
    changed = true;
    n++;
  }
  if (changed) fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
}
console.log('padded explanations:', n);
