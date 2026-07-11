import { describe, expect, it } from 'vitest';
import { diagnosticStemKey, stemAlreadyAsked } from './diagnostic-stem-dedupe';
import {
  answeredStemKeys,
  emptyDiagnosticSession,
  setCurrentDiagnosticItem,
  applyDiagnosticResponse,
} from './diagnostic-plan';

describe('diagnosticStemKey', () => {
  it('normalizes whitespace and case', () => {
    expect(diagnosticStemKey('  What is  $x^2$? ')).toBe(
      diagnosticStemKey('what is  $x^2$?'),
    );
  });
});

describe('answeredStemKeys', () => {
  it('only includes stems from submitted responses, not pending question', () => {
    let state = emptyDiagnosticSession(null, ['algebra_basics'], []);
    state = setCurrentDiagnosticItem(state, {
      id: '11111111-1111-4111-8111-111111111111',
      topic: 'algebra_basics',
      subject: 'math',
      difficulty: 4,
      stem: 'Solve $2x+1=5$.',
      options: { choices: ['1', '2', '3', '4'], correct: 'B' },
      stem_he: null,
      options_he: null,
    });
    expect(stemAlreadyAsked('Solve $2x+1=5$.', answeredStemKeys(state))).toBe(false);

    state = applyDiagnosticResponse(state, {
      item_id: '11111111-1111-4111-8111-111111111111',
      topic: 'algebra_basics',
      difficulty: 4,
      correct: true,
      chosen: 'B',
    });
    expect(stemAlreadyAsked('Solve $2x+1=5$.', answeredStemKeys(state))).toBe(true);
  });
});
