import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  deterministicItemId,
  assertStorable,
  upsertQuestionItems,
  _internal,
} from './question-store-io.mjs';
import { verifyItem, verifyPart, enqueueForReview, loadReviewQueue } from './question-verifier.mjs';
import { itemToLessonQuestions, selectBalanced, bakeConceptQuestions } from '../bake-question-items.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = JSON.parse(
  fs.readFileSync(path.join(here, '..', 'seed_data', 'question-items.sample.json'), 'utf8'),
);

test('deterministicItemId is stable and content-addressed', () => {
  const id1 = deterministicItemId('abc');
  const id2 = deterministicItemId('abc');
  const id3 = deterministicItemId('abd');
  assert.equal(id1, id2);
  assert.notEqual(id1, id3);
  assert.match(id1, /^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
});

test('assertStorable enforces the license policy', () => {
  const base = FIXTURES[1];
  assert.doesNotThrow(() => assertStorable(base));
  assert.throws(() => assertStorable({ ...base, license: 'proprietary' }), /style-reference-only/);
  assert.throws(() => assertStorable({ ...base, license: 'unknown' }), /style-reference-only/);
  assert.throws(
    () => assertStorable({ ...base, display_publicly: true, license: 'generated-original' }),
    /display_publicly is only allowed/,
  );
});

test('upsertQuestionItems normalizes + issues one write per item (fake sql)', async () => {
  const calls = [];
  const fakeSql = (strings, ...values) => {
    calls.push({ text: strings.join('?'), values });
    return Promise.resolve([]);
  };
  const ids = await upsertQuestionItems(fakeSql, FIXTURES.slice(0, 2));
  assert.equal(ids.length, 2);
  assert.equal(calls.length, 2);
  // Deterministic id derived from content is stable across runs.
  const again = await upsertQuestionItems(fakeSql, FIXTURES.slice(0, 2));
  assert.deepEqual(again, ids);
  // Normalization unions part atoms into item.skill_atoms.
  const norm = _internal.normalizeForStore(FIXTURES[2]);
  assert.deepEqual([...norm.skill_atoms].sort(), ['critical_points', 'power_rule']);
});

test('verifyPart: official key match -> auto_verified; mismatch -> rejected', async () => {
  const numericPart = FIXTURES[0].parts[0];
  const ok = await verifyPart(numericPart, { officialAnswer: 12 });
  assert.equal(ok.status, 'auto_verified');
  assert.equal(ok.method, 'official_key');
  const bad = await verifyPart(numericPart, { officialAnswer: 99 });
  assert.equal(bad.status, 'rejected');
});

test('verifyPart: CAS confirms -> auto_verified', async () => {
  const casRunner = async (part) => ({
    supported: true,
    matches: part.answer_payload?.value === 12,
    computed: 12,
  });
  const res = await verifyPart(FIXTURES[0].parts[0], { casRunner });
  assert.equal(res.status, 'auto_verified');
  assert.equal(res.method, 'cas');
});

test('verifyItem: multi-part open item needs human review', async () => {
  const verdict = await verifyItem(FIXTURES[2], {
    llmRunner: async () => ({ agreement: 0.8 }),
  });
  assert.equal(verdict.status, 'unverified');
  assert.equal(verdict.needsHumanReview, true);
});

test('human review queue round-trips (JSONL)', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'qrev-'));
  const queue = path.join(dir, 'review.jsonl');
  enqueueForReview(queue, { ...FIXTURES[2], id: 'x1' }, { confidence: 0.8, verification: {} });
  enqueueForReview(queue, { ...FIXTURES[2], id: 'x2' }, { confidence: 0.5, verification: {} });
  const loaded = loadReviewQueue(queue);
  assert.equal(loaded.length, 2);
  assert.equal(loaded[0].item_id, 'x1');
});

test('bake: composite -> lesson questions with kind diversity', () => {
  const flat = FIXTURES.flatMap(itemToLessonQuestions);
  // numeric + mcq + short_answer + derivation = 4 kinds
  assert.ok(new Set(flat.map((q) => q.kind)).size >= 3);
  // multi-part shared stem is folded into each part stem.
  const derivation = flat.find((q) => q.kind === 'derivation');
  assert.match(derivation.stem_en, /x\^3 - 3x/);

  const balanced = selectBalanced(flat, 3);
  assert.equal(balanced.length, 3);

  const { questions, warnings } = bakeConceptQuestions(FIXTURES, { max: 8 });
  assert.ok(questions.length >= 4);
  assert.deepEqual(warnings, []);
  for (const q of questions) {
    assert.ok(Array.isArray(q.skill_atoms) && q.skill_atoms.length > 0);
  }
});
