import { describe, expect, it } from 'vitest';
import { dedupeConceptIdsForCatalog, resolveConceptAlias } from './concept-aliases';

describe('dedupeConceptIdsForCatalog', () => {
  it('removes alias slug when canonical id shares the same lesson', () => {
    const ids = [
      'descriptive_statistics',
      'statistics_descriptive',
      'basic_probability',
      'probability_basic',
    ];
    const out = dedupeConceptIdsForCatalog(ids);
    expect(out).toEqual(['statistics_descriptive', 'probability_basic']);
    expect(out.every((id) => resolveConceptAlias(id) === id || id === 'probability_basic')).toBe(
      true,
    );
  });
});
