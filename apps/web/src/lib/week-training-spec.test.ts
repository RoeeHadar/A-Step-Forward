/**
 * Unit tests for week-training-spec.ts — pure derivation logic only.
 * Tests deriveTrainingSpec() and trainingSpecForAgentContext() without any DB I/O.
 * The server-only import is stubbed by vitest.config.ts alias.
 */
import { describe, expect, it } from 'vitest';
import { deriveTrainingSpec, trainingSpecForAgentContext } from './week-training-spec';
import type { WeekAtomRow } from './neon-db';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeAtomRow(
  a: string,
  mastery: number,
  is_due = false,
  concept_id = 'concept_a',
): WeekAtomRow {
  return {
    atom: a,
    mastery,
    is_due,
    concept_id,
    concept_name: concept_id.replace(/_/g, ' '),
    concept_name_he: `${concept_id}_he`,
  };
}

const BASE_WEEK = {
  id: 'week-1',
  week_number: 1,
  quiz_due_at: null,
  concepts: [{ concept_id: 'concept_a' }, { concept_id: 'concept_b' }],
} as const;

const PLAN_ID = 'plan-abc';
const FIXED_NOW = new Date('2026-07-24T12:00:00Z');

// ---------------------------------------------------------------------------
// deriveTrainingSpec — fallback / no data
// ---------------------------------------------------------------------------

describe('deriveTrainingSpec — empty data', () => {
  it('returns custom_quiz fallback when no gate, no drills, no reviews', () => {
    const spec = deriveTrainingSpec([], false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.drills).toHaveLength(0);
    expect(spec.due_reviews.count).toBe(0);
    expect(spec.gate.passed).toBe(false);
    expect(spec.recommended).toHaveLength(1);
    expect(spec.recommended[0]?.kind).toBe('custom_quiz');
  });

  it('populates week_id, plan_id, week_number correctly', () => {
    const spec = deriveTrainingSpec([], false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.week_id).toBe('week-1');
    expect(spec.plan_id).toBe(PLAN_ID);
    expect(spec.week_number).toBe(1);
  });

  it('custom_quiz href links to /app/quiz with topic ids', () => {
    const spec = deriveTrainingSpec([], false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    const action = spec.recommended[0]!;
    expect(action.href).toContain('/app/quiz');
    expect(action.href).toContain('concept_a');
  });
});

// ---------------------------------------------------------------------------
// deriveTrainingSpec — weekly gate
// ---------------------------------------------------------------------------

describe('deriveTrainingSpec — weekly gate', () => {
  it('surfaces quiz_gate action when gate is due and not passed', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    };
    const spec = deriveTrainingSpec([], false, week, PLAN_ID, FIXED_NOW);
    expect(spec.recommended[0]?.kind).toBe('quiz_gate');
  });

  it('quiz_gate href contains plan_id and week_num', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 86_400_000).toISOString(),
    };
    const spec = deriveTrainingSpec([], false, week, PLAN_ID, FIXED_NOW);
    const gate = spec.recommended.find((a) => a.kind === 'quiz_gate');
    expect(gate).toBeDefined();
    expect(gate?.href).toContain(PLAN_ID);
    expect(gate?.href).toContain('week_num=1');
    expect(gate?.href).toContain('/quiz/week-1');
  });

  it('does NOT surface quiz_gate when gate is already passed', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 86_400_000).toISOString(),
    };
    const spec = deriveTrainingSpec([], true, week, PLAN_ID, FIXED_NOW);
    const gate = spec.recommended.find((a) => a.kind === 'quiz_gate');
    expect(gate).toBeUndefined();
  });

  it('surface custom_quiz celebration when gate passed and no drills', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 86_400_000).toISOString(),
    };
    const spec = deriveTrainingSpec([], true, week, PLAN_ID, FIXED_NOW);
    const quizAction = spec.recommended.find((a) => a.kind === 'custom_quiz');
    expect(quizAction).toBeDefined();
    expect(quizAction?.reason_en).toContain('Gate passed');
  });

  it('reason_he is "due soon" flavour when gate expires within 3 days', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 2 * 60 * 60 * 1000).toISOString(), // 2h away
    };
    const spec = deriveTrainingSpec([], false, week, PLAN_ID, FIXED_NOW);
    const gate = spec.recommended.find((a) => a.kind === 'quiz_gate');
    expect(gate?.reason_en).toContain('due soon');
  });
});

// ---------------------------------------------------------------------------
// deriveTrainingSpec — drills
// ---------------------------------------------------------------------------

describe('deriveTrainingSpec — drills', () => {
  it('surfaces drill action when atom mastery < 0.6', () => {
    const rows = [makeAtomRow('weak_atom', 0.2)];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.drills).toHaveLength(1);
    expect(spec.drills[0]?.mastery).toBe(0.2);
    const drillAction = spec.recommended.find((a) => a.kind === 'drill');
    expect(drillAction).toBeDefined();
    expect(drillAction?.href).toContain('/app/practice');
    expect(drillAction?.href).toContain('topics=');
  });

  it('does NOT surface drill when atom mastery >= 0.6', () => {
    const rows = [makeAtomRow('strong_atom', 0.65)];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.drills).toHaveLength(0);
    expect(spec.recommended.find((a) => a.kind === 'drill')).toBeUndefined();
  });

  it('sorts drills ascending by mastery (weakest first)', () => {
    const rows = [
      makeAtomRow('atom_b', 0.4, false, 'concept_b'),
      makeAtomRow('atom_a', 0.1, false, 'concept_a'),
    ];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.drills[0]?.atom).toBe('atom_a');
    expect(spec.drills[1]?.atom).toBe('atom_b');
  });

  it('caps drills at 6', () => {
    const rows = Array.from({ length: 10 }, (_, i) =>
      makeAtomRow(`atom_${i}`, i * 0.05, false, 'concept_a'),
    );
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.drills.length).toBeLessThanOrEqual(6);
  });
});

// ---------------------------------------------------------------------------
// deriveTrainingSpec — FSRS due reviews
// ---------------------------------------------------------------------------

describe('deriveTrainingSpec — due reviews', () => {
  it('surfaces review action when atoms are FSRS-due', () => {
    const rows = [makeAtomRow('due_atom', 0.8, true)];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.due_reviews.count).toBe(1);
    const reviewAction = spec.recommended.find((a) => a.kind === 'review');
    expect(reviewAction).toBeDefined();
    expect(reviewAction?.href).toContain('mode=due');
  });

  it('groups due atoms by concept (deduplicates)', () => {
    const rows = [
      makeAtomRow('atom_1', 0.8, true, 'concept_a'),
      makeAtomRow('atom_2', 0.7, true, 'concept_a'),
    ];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.due_reviews.count).toBe(2);
    expect(spec.due_reviews.top_concepts).toHaveLength(1);
    expect(spec.due_reviews.top_concepts[0]?.concept_id).toBe('concept_a');
  });

  it('atom with mastery >= 0.6 but is_due contributes to reviews but not drills', () => {
    const rows = [makeAtomRow('reviewed_atom', 0.75, true)];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(spec.drills).toHaveLength(0);
    expect(spec.due_reviews.count).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// deriveTrainingSpec — ordering + cap
// ---------------------------------------------------------------------------

describe('deriveTrainingSpec — ordering and cap', () => {
  it('quiz_gate comes first before drill and review', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 86_400_000).toISOString(),
    };
    const rows = [
      makeAtomRow('weak', 0.2, true),
    ];
    const spec = deriveTrainingSpec(rows, false, week, PLAN_ID, FIXED_NOW);
    expect(spec.recommended[0]?.kind).toBe('quiz_gate');
  });

  it('limits recommended to at most 4', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: new Date(FIXED_NOW.getTime() + 86_400_000).toISOString(),
    };
    const rows = Array.from({ length: 8 }, (_, i) =>
      makeAtomRow(`a${i}`, 0.1, i % 2 === 0, 'concept_a'),
    );
    const spec = deriveTrainingSpec(rows, false, week, PLAN_ID, FIXED_NOW);
    expect(spec.recommended.length).toBeLessThanOrEqual(4);
  });
});

// ---------------------------------------------------------------------------
// trainingSpecForAgentContext
// ---------------------------------------------------------------------------

describe('trainingSpecForAgentContext', () => {
  it('returns a string of ≤600 chars', () => {
    const spec = deriveTrainingSpec([], false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    const ctx = trainingSpecForAgentContext(spec);
    expect(typeof ctx).toBe('string');
    expect(ctx.length).toBeLessThanOrEqual(600);
  });

  it('includes week number', () => {
    const spec = deriveTrainingSpec([], false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(trainingSpecForAgentContext(spec)).toContain('Week 1');
  });

  it('includes no-gate when no gate date', () => {
    const spec = deriveTrainingSpec([], false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(trainingSpecForAgentContext(spec)).toContain('no-gate');
  });

  it('includes gate due date when gate is set', () => {
    const week = {
      ...BASE_WEEK,
      quiz_due_at: '2026-07-31T12:00:00Z',
    };
    const spec = deriveTrainingSpec([], false, week, PLAN_ID, FIXED_NOW);
    expect(trainingSpecForAgentContext(spec)).toContain('due:2026-07-31');
  });

  it('includes passed when gate passed', () => {
    const week = { ...BASE_WEEK, quiz_due_at: '2026-07-31T12:00:00Z' };
    const spec = deriveTrainingSpec([], true, week, PLAN_ID, FIXED_NOW);
    expect(trainingSpecForAgentContext(spec)).toContain('passed');
  });

  it('includes drill atoms with mastery % notation', () => {
    const rows = [makeAtomRow('my_atom', 0.25)];
    const spec = deriveTrainingSpec(rows, false, BASE_WEEK, PLAN_ID, FIXED_NOW);
    expect(trainingSpecForAgentContext(spec)).toContain('my_atom@25%');
  });

  it('truncates to 600 chars when content is very long', () => {
    const longWeek = {
      id: 'x'.repeat(100),
      week_number: 99,
      quiz_due_at: '2026-07-31T12:00:00Z',
      concepts: Array.from({ length: 20 }, (_, i) => ({ concept_id: `concept_${'x'.repeat(30)}_${i}` })),
    };
    const rows = Array.from({ length: 6 }, (_, i) =>
      makeAtomRow(`${'very_long_atom_name_'.repeat(3)}${i}`, 0.1, false, 'concept_a'),
    );
    const spec = deriveTrainingSpec(rows, false, longWeek, PLAN_ID, FIXED_NOW);
    const ctx = trainingSpecForAgentContext(spec);
    expect(ctx.length).toBeLessThanOrEqual(600);
  });
});
