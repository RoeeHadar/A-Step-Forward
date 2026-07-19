import { describe, expect, it } from 'vitest';
import { scoreWeeklyQuizAnswers, normalizeWeeklyMcqOptions } from './weekly-quiz';
import { GATE_BANK_FORMAT_VERSION } from './gate-question-bank';
import type { StoredWeeklyQuestion } from './weekly-quiz';

function mcq(
  id: string,
  topic: string,
  correct: string,
): StoredWeeklyQuestion {
  return {
    id,
    topic,
    subject: 'math',
    difficulty: 0.8,
    kind: 'mcq',
    stem: `${id}?`,
    options: [
      { key: 'A', text: '3' },
      { key: 'B', text: '4' },
      { key: 'C', text: '5' },
      { key: 'D', text: '6' },
    ],
    correct,
    source: 'lesson_bank',
    format_version: GATE_BANK_FORMAT_VERSION,
  };
}

describe('scoreWeeklyQuizAnswers', () => {
  const questions: StoredWeeklyQuestion[] = [
    mcq('q1', 'algebra_basics', 'B'),
    mcq('q2', 'algebra_basics', 'B'),
    {
      id: 'q3',
      topic: 'geometry_intro',
      subject: 'math',
      difficulty: 0.9,
      kind: 'numeric',
      stem: 'Area?',
      options: [],
      correct_answer: '12',
      source: 'lesson_bank',
      format_version: GATE_BANK_FORMAT_VERSION,
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

  it('grades numeric answers', () => {
    const result = scoreWeeklyQuizAnswers(questions, [
      { item_id: 'q1', chosen: 'B' },
      { item_id: 'q2', chosen: 'B' },
      { item_id: 'q3', chosen: '12' },
    ]);
    expect(result.score).toBe(1);
  });

  it('uses openGrades for open items (fail-closed without grade)', () => {
    const openQ: StoredWeeklyQuestion[] = [
      {
        id: 'o1',
        topic: 'derivatives_rules',
        subject: 'math',
        difficulty: 0.9,
        kind: 'open',
        stem: 'Prove…',
        options: [],
        rubric: 'Must use chain rule',
        source: 'lesson_bank',
        format_version: GATE_BANK_FORMAT_VERSION,
      },
    ];
    expect(scoreWeeklyQuizAnswers(openQ, [{ item_id: 'o1', chosen: 'because' }]).score).toBe(0);
    expect(
      scoreWeeklyQuizAnswers(openQ, [{ item_id: 'o1', chosen: 'full proof' }], { o1: true }).score,
    ).toBe(1);
  });

  it('returns zero for empty answers', () => {
    const result = scoreWeeklyQuizAnswers(questions, []);
    expect(result.score).toBe(0);
  });
});

describe('normalizeWeeklyMcqOptions', () => {
  it('maps numeric option keys to A–D letters', () => {
    const normalized = normalizeWeeklyMcqOptions(
      [
        { key: '1', text: 'a' },
        { key: '2', text: 'b' },
        { key: '3', text: 'c' },
        { key: '4', text: 'd' },
      ],
      '2',
    );
    expect(normalized?.correct).toBe('B');
    expect(normalized?.options.map((o) => o.key)).toEqual(['A', 'B', 'C', 'D']);
  });
});
