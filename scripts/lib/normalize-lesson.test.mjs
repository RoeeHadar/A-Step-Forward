import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  acceptableAnswersLookBroken,
  agentHintsIsStructured,
  validateLessonStrict,
} from './normalize-lesson.mjs';

test('acceptableAnswersLookBroken flags empty / artifact / bare-token lists', () => {
  assert.equal(acceptableAnswersLookBroken([]), true);
  assert.equal(acceptableAnswersLookBroken(null), true);
  assert.equal(acceptableAnswersLookBroken(['']), true);
  assert.equal(acceptableAnswersLookBroken(['6']), true, 'bare 1-char token is unusable');
  assert.equal(
    acceptableAnswersLookBroken(['Re-substitute or verify units']),
    true,
    'known filler artifact',
  );
  assert.equal(acceptableAnswersLookBroken(["f'(x) = 28x^3 - 6x"]), false);
});

test('agentHintsIsStructured accepts objects, rejects strings/arrays', () => {
  assert.equal(agentHintsIsStructured('some string'), false);
  assert.equal(agentHintsIsStructured(['a']), false);
  assert.equal(agentHintsIsStructured(null), false);
  assert.equal(agentHintsIsStructured({ skill_atoms_unlocked: ['a'] }), true);
  assert.equal(agentHintsIsStructured({ key_insights: [] }), true);
});

test('validateLessonStrict catches unstructured hints, empty atoms, low variety', () => {
  const lesson = {
    concept_id: 'demo',
    subject: 'math',
    level: 'high_school',
    title_en: 'Demo',
    title_he: 'הדגמה',
    summary_en: 'x',
    summary_he: 'x',
    sections: [],
    agent_hints: 'a plain string',
    questions: [
      { kind: 'short_answer', skill_atoms: [], answer_payload: { acceptable_answers: ['6'] } },
    ],
  };
  const errors = validateLessonStrict('demo.json', lesson);
  assert.ok(errors.some((e) => e.includes('agent_hints must be a structured object')));
  assert.ok(errors.some((e) => e.includes('must exercise >=1 skill_atom')));
  assert.ok(errors.some((e) => e.includes('acceptable_answers look broken')));
  assert.ok(errors.some((e) => e.includes('question-kind diversity too low')));
});
