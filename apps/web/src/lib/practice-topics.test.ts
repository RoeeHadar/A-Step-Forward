import { describe, expect, it } from 'vitest';
import {
  conceptIdsForTopics,
  parsePracticeTopicIds,
  PRACTICE_TOPICS,
  practiceTopicsByGroup,
} from './practice-topics';

describe('practice-topics', () => {
  it('exposes curated topics with concept membership', () => {
    expect(PRACTICE_TOPICS.length).toBeGreaterThanOrEqual(15);
    expect(parsePracticeTopicIds(['functions', 'nope', 'geometry'])).toEqual([
      'functions',
      'geometry',
    ]);
    const ids = conceptIdsForTopics(['functions']);
    expect(ids).toContain('functions_intro');
  });

  it('groups topics for the picker', () => {
    const groups = practiceTopicsByGroup('en');
    expect(groups.some((g) => g.group === 'Math')).toBe(true);
    expect(groups.some((g) => g.group === 'Physics')).toBe(true);
  });
});
