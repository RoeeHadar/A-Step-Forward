import { describe, expect, it } from 'vitest';
import { scoreWeeklyQuizAnswers, normalizeWeeklyMcqOptions } from './weekly-quiz';

describe('scoreWeeklyQuizAnswers', () => {
  const questions = [
    {
      id: 'q1',
      topic: 'algebra_basics',
      subject: 'math',
      difficulty: 0.5,
      stem: '2+2?',
      options: [
        { key: 'A', text: '3' },
        { key: 'B', text: '4' },
        { key: 'C', text: '5' },
        { key: 'D', text: '6' },
      ],
      correct: 'B',
    },
    {
      id: 'q2',
      topic: 'algebra_basics',
      subject: 'math',
      difficulty: 0.6,
      stem: '3+3?',
      options: [
        { key: 'A', text: '5' },
        { key: 'B', text: '6' },
        { key: 'C', text: '7' },
        { key: 'D', text: '8' },
      ],
      correct: 'B',
    },
    {
      id: 'q3',
      topic: 'geometry_intro',
      subject: 'math',
      difficulty: 0.4,
      stem: 'Square sides?',
      options: [
        { key: 'A', text: '3' },
        { key: 'B', text: '4' },
        { key: 'C', text: '5' },
        { key: 'D', text: '6' },
      ],
      correct: 'B',
    },
  ];

  it('scores answered items; unanswered count as wrong', () => {
    const result = scoreWeeklyQuizAnswers(questions, [
      { item_id: 'q1', chosen: 'B' },
      { item_id: 'q2', chosen: 'A' },
    ]);
    expect(result.score).toBeCloseTo(1 / 3, 4);
    expect(result.per_topic.algebra_basics).toBeCloseTo(0.5, 4);
    expect(result.per_topic.geometry_intro).toBe(0);
    expect(result.weak_concepts).toContain('geometry_intro');
  });

  it('returns perfect score when all correct', () => {
    const result = scoreWeeklyQuizAnswers(questions, [
      { item_id: 'q1', chosen: 'b' },
      { item_id: 'q2', chosen: 'B' },
      { item_id: 'q3', chosen: 'B' },
    ]);
    expect(result.score).toBe(1);
    expect(result.weak_concepts).toHaveLength(0);
  });

  it('returns zero for empty answers', () => {
    const result = scoreWeeklyQuizAnswers(questions, []);
    expect(result.score).toBe(0);
    expect(Object.values(result.per_topic).every((s) => s === 0)).toBe(true);
  });
});

describe('normalizeWeeklyMcqOptions', () => {
  it('maps numeric option keys to A–D letters', () => {
    const normalized = normalizeWeeklyMcqOptions(
      [
        { key: '1', text: 'one' },
        { key: '2', text: 'two' },
        { key: '3', text: 'three' },
        { key: '4', text: 'four' },
      ],
      '2',
    );
    expect(normalized?.correct).toBe('B');
    expect(normalized?.options.map((o) => o.key)).toEqual(['A', 'B', 'C', 'D']);
  });
});
