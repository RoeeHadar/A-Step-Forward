#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const DEFAULTS = {
  sequences: ['arithmetic_sequence', 'series_sum', 'sequence_term'],
  function: ['function_analysis', 'derivative_sign', 'graph_reading'],
  derivative: ['derivative_rules', 'critical_points', 'optimization'],
  optim: ['optimization', 'critical_points', 'related_rates'],
};

function defaultsFor(id) {
  if (/sequence/i.test(id)) return DEFAULTS.sequences;
  if (/optim/i.test(id)) return DEFAULTS.optim;
  if (/derivative|function_analysis/i.test(id)) return DEFAULTS.derivative;
  if (/function/i.test(id)) return DEFAULTS.function;
  return ['core_skill'];
}

let n = 0;
for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith('.json'))) {
  const fp = path.join(DIR, f);
  const j = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const fallback = (j.skill_atom_bank && j.skill_atom_bank.length
    ? j.skill_atom_bank
    : defaultsFor(j.concept_id || f)).slice(0, 2);
  let changed = false;
  for (const q of j.questions || []) {
    if (!Array.isArray(q.skill_atoms) || q.skill_atoms.length === 0) {
      q.skill_atoms = [...fallback];
      changed = true;
      n++;
    }
  }
  if (changed) {
    if (!j.skill_atom_bank || j.skill_atom_bank.length === 0) {
      j.skill_atom_bank = [...fallback];
    }
    fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
    console.log('backfilled', f);
  }
}
console.log('questions fixed:', n);
