import { test } from 'node:test';
import assert from 'node:assert/strict';
import { evalExpr, verifyQuestion } from './verify-question.mjs';

test('evalExpr: arithmetic + precedence', () => {
  assert.equal(evalExpr('2 + 2*3'), 8);
  assert.equal(evalExpr('(2 + 2)*3'), 12);
  assert.equal(evalExpr('2^3^2'), 512); // right-assoc
  assert.equal(evalExpr('-2^2'), -4); // unary applies to result of pow
  assert.equal(evalExpr('10 % 3'), 1);
});

test('evalExpr: functions + constants', () => {
  assert.equal(evalExpr('sqrt(16)'), 4);
  assert.equal(evalExpr('choose(5,2)'), 10);
  assert.equal(evalExpr('fact(5)'), 120);
  assert.ok(Math.abs(evalExpr('sin(pi/2)') - 1) < 1e-9);
  assert.ok(Math.abs(evalExpr('log(1000)') - 3) < 1e-9);
});

test('evalExpr: variable scope + numeric derivative', () => {
  assert.equal(evalExpr('x^2', { x: 3 }), 9);
  assert.ok(Math.abs(evalExpr('deriv(x^2, x, 3)') - 6) < 1e-3);
  assert.ok(Math.abs(evalExpr('deriv(sin(x), x, 0)') - 1) < 1e-3);
});

test('evalExpr: rejects unknown symbols', () => {
  assert.throws(() => evalExpr('foo(2)'));
  assert.throws(() => evalExpr('y + 1'));
});

test('verifyQuestion: Tier-1 verify block matches', () => {
  const q = { kind: 'numeric', correct_answer: 8, verify: { expr: '2 + 2*3', expected: 8 } };
  assert.deepEqual(verifyQuestion(q), { checked: true, ok: true });
});

test('verifyQuestion: Tier-1 mismatch fails', () => {
  const q = { kind: 'numeric', correct_answer: 9, verify: { expr: '2 + 2*3', expected: 8 } };
  const r = verifyQuestion(q);
  assert.equal(r.ok, false);
});

test('verifyQuestion: non-verifiable needs review + worked solution', () => {
  const bare = { kind: 'derivation' };
  assert.equal(verifyQuestion(bare).ok, false);

  const flaggedThin = { kind: 'derivation', needs_review: true, explanation_en: 'Use the rule.' };
  assert.equal(verifyQuestion(flaggedThin).ok, false);

  const good = {
    kind: 'derivation',
    needs_review: true,
    explanation_en:
      'Step 1: apply the power rule to each term. Step 2: differentiate the constant, which is zero. Step 3: combine the terms to get the final derivative expression.',
    explanation_he: 'שלב 1: נגזור כל איבר. שלב 2: הקבוע מתאפס. שלב 3: נחבר את האיברים לתוצאה הסופית.',
  };
  assert.equal(verifyQuestion(good).ok, true);
});

test('verifyQuestion: deterministic kind without verify passes', () => {
  assert.equal(verifyQuestion({ kind: 'mcq' }).ok, true);
});
