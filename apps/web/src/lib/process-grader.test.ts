import { describe, expect, it } from 'vitest';
import { aggregateProcessScores, perTopicFromItemScores } from './process-grader';

describe('process-grader aggregation', () => {
  it('averages item process scores', () => {
    expect(aggregateProcessScores(['a', 'b'], { a: 1, b: 0.5 })).toBe(0.75);
  });

  it('treats missing scores as 0', () => {
    expect(aggregateProcessScores(['a', 'b', 'c'], { a: 1 })).toBe(0.3333);
  });

  it('returns 0 for empty id list', () => {
    expect(aggregateProcessScores([], { a: 1 })).toBe(0);
  });

  it('aggregates per-topic means', () => {
    const per = perTopicFromItemScores(
      [
        { id: '1', topic: 'derivatives' },
        { id: '2', topic: 'derivatives' },
        { id: '3', topic: 'integrals' },
      ],
      { '1': 1, '2': 0.5, '3': 0 },
    );
    expect(per.derivatives).toBe(0.75);
    expect(per.integrals).toBe(0);
  });
});
