import { describe, expect, it } from 'vitest';
import {
  buildRevealMap,
  gradeClosedFromStoredOnly,
  stripCustomQuizForClient,
} from './custom-quiz-strip';
import type { CustomQuizEnvelope, CustomQuizQuestion } from './quiz-builder';

const sampleQ: CustomQuizQuestion & { id: string } = {
  id: 'q1',
  ord: 1,
  kind: 'mcq',
  difficulty: 'medium',
  concept_id: 'derivatives_rules',
  skill_atoms: [],
  stem_en: 'Pick',
  stem_he: 'בחר',
  total_points: 5,
  sample_solution_en: 'SECRET EN',
  sample_solution_he: 'SECRET HE',
  rubric_en: 'RUBRIC EN',
  rubric_he: 'RUBRIC HE',
  options_en: ['a', 'b', 'c'],
  options_he: ['א', 'ב', 'ג'],
  correct_index: 1,
  explanation_en: 'because',
};

const envelope: CustomQuizEnvelope & {
  questions: Array<CustomQuizQuestion & { id: string }>;
} = {
  quiz_id: 'will-be-overwritten',
  kind_mix: 'open',
  mode: 'bagrut_open',
  time_limit_s: 1200,
  concepts: [],
  questions: [sampleQ],
  picked_reason: 'user_topics',
};

describe('stripCustomQuizForClient', () => {
  it('removes answer keys and solutions from the start envelope', () => {
    const pub = stripCustomQuizForClient(envelope);
    expect(pub.questions).toHaveLength(1);
    const q = pub.questions[0] as Record<string, unknown>;
    expect(q.id).toBe('q1');
    expect(q.stem_en).toBe('Pick');
    expect(q.options_en).toEqual(['a', 'b', 'c']);
    expect(q).not.toHaveProperty('correct_index');
    expect(q).not.toHaveProperty('sample_solution_en');
    expect(q).not.toHaveProperty('sample_solution_he');
    expect(q).not.toHaveProperty('rubric_en');
    expect(q).not.toHaveProperty('explanation_en');
  });
});

describe('gradeClosedFromStoredOnly', () => {
  it('ignores forged client correct letter', () => {
    expect(gradeClosedFromStoredOnly({ kind: 'mcq', correct_index: 1 }, 'B')).toBe(1);
    expect(gradeClosedFromStoredOnly({ kind: 'mcq', correct_index: 1 }, 'A')).toBe(0);
  });
});

describe('buildRevealMap', () => {
  it('exposes solutions keyed by question id', () => {
    const reveal = buildRevealMap([sampleQ]);
    expect(reveal.q1?.sample_solution_en).toBe('SECRET EN');
    expect(reveal.q1?.correct_index).toBe(1);
  });
});
