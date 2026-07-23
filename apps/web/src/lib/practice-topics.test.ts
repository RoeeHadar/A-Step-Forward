import { describe, expect, it } from 'vitest';
import {
  conceptIdsForTopics,
  parsePracticeTopicIds,
  PRACTICE_TOPICS,
} from './practice-topics';

describe('practice-topics', () => {
  it('exposes curated topics with concept membership', () => {
    expect(PRACTICE_TOPICS.length).toBeGreaterThanOrEqual(5);
    expect(parsePracticeTopicIds(['functions', 'nope', 'geometry'])).toEqual([
      'functions',
      'geometry',
    ]);
    const ids = conceptIdsForTopics(['functions']);
    expect(ids).toContain('functions_intro');
  });
});
