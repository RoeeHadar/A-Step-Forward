import { test } from 'node:test';
import assert from 'node:assert/strict';
import { coerceAtomId, collectLessonAtoms } from './skill-atoms.mjs';

test('string atoms pass through without warning', () => {
  const warns = [];
  assert.equal(coerceAtomId('electric_flux', 'x', (m) => warns.push(m)), 'electric_flux');
  assert.deepEqual(warns, []);
});

test('object atoms are coerced to their id with a warning', () => {
  const warns = [];
  const obj = { id: 'electric_flux', label_en: 'electric_flux', label_he: 'electric_flux' };
  assert.equal(coerceAtomId(obj, 'f.json', (m) => warns.push(m)), 'electric_flux');
  assert.equal(warns.length, 1);
  assert.match(warns[0], /coerced object atom to id "electric_flux" \(f\.json\)/);
});

test('atoms without a usable id are rejected', () => {
  for (const bad of [null, 42, {}, { id: '' }, { id: 7 }]) {
    assert.throws(() => coerceAtomId(bad, '', () => {}), TypeError);
  }
});

test('collectLessonAtoms dedupes by id, never by object identity', () => {
  const o = () => ({ id: 'biot_savart', label_en: 'b', label_he: 'b' });
  const data = {
    agent_hints: { skill_atoms_unlocked: ['biot_savart'] },
    questions: [{ skill_atoms: [o(), 'magnetic_force'] }, { skill_atoms: [o()] }],
  };
  const r = collectLessonAtoms(data, '', () => {});
  assert.deepEqual([...r.all].sort(), ['biot_savart', 'magnetic_force']);
  assert.deepEqual([...r.taught], ['biot_savart']);
  for (const a of r.all) assert.equal(typeof a, 'string');
});
