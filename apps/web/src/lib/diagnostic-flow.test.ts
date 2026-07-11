import { describe, expect, it } from 'vitest';
import {
  applyDiagnosticResponse,
  answeredItemIds,
  answeredStemKeys,
  buildValidationQueue,
  emptyDiagnosticSession,
  isDiagnosticSessionComplete,
  parseDiagnosticSessionPayload,
  resolveCurrentDiagnosticItem,
  setCurrentDiagnosticItem,
  type DiagnosticServedItem,
} from './diagnostic-plan';
import { DIAGNOSTIC_QUESTIONS_PER_SESSION } from './diagnostic-start';
import { pickDiagnosticItemFromLessonBank } from './diagnostic-lesson-bank';
import { stemAlreadyAsked } from './diagnostic-stem-dedupe';

const profile4pt = {
  subjects: ['math'],
  points_group: '4pt',
} as never;

function mockItem(
  id: string,
  topic: string,
  stem: string,
): DiagnosticServedItem {
  return {
    id,
    topic,
    subject: 'math',
    difficulty: 5,
    stem,
    options: { choices: ['1', '2', '3', '4'], correct: 'A' },
    stem_he: null,
    options_he: null,
  };
}

describe('diagnostic session flow (serve vs answer)', () => {
  it('does not mark stems as asked when a question is only shown', () => {
    const queue = buildValidationQueue(['algebra_basics', 'factoring'], { algebra_basics: 3 }, 2);
    let state = emptyDiagnosticSession(null, ['algebra_basics'], queue);
    const item = mockItem('q1', 'algebra_basics', 'Solve $2x+1=5$.');

    state = setCurrentDiagnosticItem(state, item);

    expect(answeredItemIds(state)).toEqual([]);
    expect(answeredStemKeys(state)).toEqual([]);
    expect(stemAlreadyAsked(item.stem, answeredStemKeys(state))).toBe(false);
    expect(isDiagnosticSessionComplete(state)).toBe(false);
    expect(resolveCurrentDiagnosticItem(state)?.id).toBe('q1');
  });

  it('resumes the pending question after a page reload', () => {
    const queue = buildValidationQueue(['algebra_basics'], { algebra_basics: 5 }, 1);
    let state = emptyDiagnosticSession(null, ['algebra_basics'], queue);
    state = setCurrentDiagnosticItem(
      state,
      mockItem('pending-id', 'algebra_basics', 'What is $3+4$?'),
    );

    const pending = resolveCurrentDiagnosticItem(state);
    expect(pending?.stem).toBe('What is $3+4$?');
    expect(state.responses).toHaveLength(0);
  });

  it('completes only after answers, not after advancing queue_index alone', () => {
    const queue = buildValidationQueue(['algebra_basics', 'factoring'], { algebra_basics: 3 }, 2);
    let state = emptyDiagnosticSession(null, ['algebra_basics', 'factoring'], queue);

    state = setCurrentDiagnosticItem(
      state,
      mockItem('a', 'algebra_basics', 'Stem A'),
    );
    state = applyDiagnosticResponse(state, {
      item_id: 'a',
      topic: 'algebra_basics',
      difficulty: 4,
      correct: true,
      chosen: 'A',
    });

    expect(isDiagnosticSessionComplete(state)).toBe(false);

    state = setCurrentDiagnosticItem(state, mockItem('b', 'factoring', 'Stem B'));
    state = applyDiagnosticResponse(state, {
      item_id: 'b',
      topic: 'factoring',
      difficulty: 5,
      correct: false,
      chosen: 'B',
    });

    expect(isDiagnosticSessionComplete(state)).toBe(true);
  });

  it('rejects v3 sessions that reserved all stems but have zero responses', () => {
    const parsed = parseDiagnosticSessionPayload({
      version: 3,
      goal_concept_id: null,
      probe_concepts: ['algebra_basics'],
      validation_queue: [
        { concept_id: 'algebra_basics', target_difficulty: 3, slot_kind: 'basic' },
      ],
      queue_index: 1,
      responses: [],
      asked_item_ids: ['old-id'],
      asked_stem_keys: ['solve 2x+1=5'],
      served_items: {},
    });

    expect(parsed).not.toBeNull();
    expect(isDiagnosticSessionComplete(parsed!)).toBe(false);
    expect(parsed!.responses).toHaveLength(0);
  });
});

describe('full validation queue walkthrough', () => {
  it(`runs ${DIAGNOSTIC_QUESTIONS_PER_SESSION} unique slots without premature completion`, () => {
    const concepts = [
      'algebra_basics',
      'equations_quadratic',
      'functions_quadratic',
      'factoring',
      'triangles_congruence',
      'circles',
    ];
    const selfScores = Object.fromEntries(
      concepts.map((c, i) => [c, i % 3 === 0 ? 3 : i % 3 === 1 ? 6 : 9]),
    );
    const queue = buildValidationQueue(concepts, selfScores, DIAGNOSTIC_QUESTIONS_PER_SESSION);
    expect(queue).toHaveLength(DIAGNOSTIC_QUESTIONS_PER_SESSION);

    let state = emptyDiagnosticSession('functions_quadratic', concepts, queue);
    const seenStems = new Set<string>();

    for (let i = 0; i < queue.length; i += 1) {
      expect(isDiagnosticSessionComplete(state)).toBe(false);
      const slot = queue[i]!;
      const item = mockItem(`item-${i}`, slot.concept_id, `Unique stem ${i} for ${slot.concept_id}`);
      state = setCurrentDiagnosticItem(state, item);
      expect(resolveCurrentDiagnosticItem(state)?.id).toBe(`item-${i}`);

      state = applyDiagnosticResponse(state, {
        item_id: `item-${i}`,
        topic: slot.concept_id,
        difficulty: slot.target_difficulty,
        correct: i % 2 === 0,
        chosen: 'A',
      });
      seenStems.add(item.stem);
    }

    expect(seenStems.size).toBe(DIAGNOSTIC_QUESTIONS_PER_SESSION);
    expect(isDiagnosticSessionComplete(state)).toBe(true);
    expect(state.responses).toHaveLength(DIAGNOSTIC_QUESTIONS_PER_SESSION);
  });
});

describe('lesson bank coverage for onboarding concepts', () => {
  const SLOT_KINDS = ['basic', 'medium', 'hard', 'verbal', 'edge'] as const;

  function pickAnyKind(conceptId: string) {
    for (const kind of SLOT_KINDS) {
      const item = pickDiagnosticItemFromLessonBank(conceptId, profile4pt, [], 5, kind);
      if (item?.stem?.trim()) return item;
    }
    return null;
  }

  it('finds MCQs for foundational concepts that appear in diagnostics', () => {
    expect(pickAnyKind('algebra_basics')).not.toBeNull();
    expect(pickAnyKind('equations_linear')).not.toBeNull();
    expect(pickAnyKind('arithmetic')).not.toBeNull();
  });
});
