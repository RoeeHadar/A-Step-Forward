import { describe, expect, it } from 'vitest';
import { diagnosticStemKey, stemAlreadyAsked } from './diagnostic-stem-dedupe';
import { reserveAskedItem, emptyDiagnosticSession } from './diagnostic-plan';

describe('diagnosticStemKey', () => {
  it('normalizes whitespace and case', () => {
    expect(diagnosticStemKey('  What is  $x^2$? ')).toBe(
      diagnosticStemKey('what is  $x^2$?'),
    );
  });
});

describe('reserveAskedItem', () => {
  it('blocks the same stem under a different item id', () => {
    let state = emptyDiagnosticSession(null, ['algebra_basics'], []);
    state = reserveAskedItem(state, {
      id: '11111111-1111-4111-8111-111111111111',
      stem: 'Solve $2x+1=5$.',
    });
    expect(
      stemAlreadyAsked('Solve $2x+1=5$.', state.asked_stem_keys),
    ).toBe(true);
    expect(
      stemAlreadyAsked('Solve $2x+1=5$.', state.asked_stem_keys) ||
        state.asked_item_ids.includes('22222222-2222-4222-8222-222222222222'),
    ).toBe(true);
  });
});
