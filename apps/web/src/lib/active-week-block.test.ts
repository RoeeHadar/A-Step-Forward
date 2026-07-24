/**
 * Unit tests for active-week-block.ts — pure formatting only, no IO.
 * Tests that the block renders correctly and stays within size limits.
 */
import { describe, expect, it } from 'vitest';
import { buildActiveWeekBlock } from './active-week-block';
import type { ActiveWeekBlockParams, ActiveWeekConcept } from './active-week-block';
import type { WeekTrainingSpec } from './week-training-spec';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeConcept(
  concept_id: string,
  opts: { mastery?: number; kind?: string; name_he?: string | null } = {},
): ActiveWeekConcept {
  return {
    concept_id,
    name: concept_id.replace(/_/g, ' '),
    name_he: opts.name_he !== undefined ? opts.name_he : null,
    mastery: opts.mastery ?? null,
    kind: opts.kind,
  };
}

function makeSpec(overrides: Partial<WeekTrainingSpec> = {}): WeekTrainingSpec {
  return {
    week_id: 'week-1',
    plan_id: 'plan-abc',
    week_number: 1,
    drills: [],
    due_reviews: { count: 0, top_concepts: [] },
    gate: { due_at: null, passed: false },
    recommended: [
      {
        kind: 'custom_quiz',
        label_he: 'חידון על נושאי השבוע',
        label_en: "Quiz on this week's topics",
        href: '/app/quiz?topics=concept_a',
        reason_he: 'בדוק/י את עצמך',
        reason_en: 'Test yourself',
      },
    ],
    ...overrides,
  };
}

function makeParams(overrides: Partial<ActiveWeekBlockParams> = {}): ActiveWeekBlockParams {
  return {
    weekNumber: 3,
    concepts: [
      makeConcept('derivatives_intro', { mastery: 0.45, name_he: 'נגזרת - מבוא' }),
      makeConcept('limits', { mastery: 0.72, name_he: 'גבולות' }),
    ],
    spec: makeSpec(),
    planHealth: { needs_replan: false, overflow_count: 0 },
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Basic rendering
// ---------------------------------------------------------------------------

describe('buildActiveWeekBlock — basic rendering', () => {
  it('starts with "## Active week"', () => {
    const block = buildActiveWeekBlock(makeParams());
    expect(block.startsWith('## Active week')).toBe(true);
  });

  it('includes the week number', () => {
    const block = buildActiveWeekBlock(makeParams({ weekNumber: 5 }));
    expect(block).toContain('Week 5');
  });

  it('includes concept ids and Hebrew names', () => {
    const block = buildActiveWeekBlock(makeParams());
    expect(block).toContain('derivatives_intro');
    expect(block).toContain('נגזרת - מבוא');
    expect(block).toContain('גבולות');
  });

  it('includes mastery percentages', () => {
    const block = buildActiveWeekBlock(makeParams());
    expect(block).toContain('~45%');
    expect(block).toContain('~72%');
  });

  it('renders English concept name when name_he is null', () => {
    const params = makeParams({
      concepts: [makeConcept('vectors', { mastery: 0.6, name_he: null })],
    });
    const block = buildActiveWeekBlock(params);
    expect(block).toContain('vectors');
  });

  it('includes recommended actions with hrefs', () => {
    const block = buildActiveWeekBlock(makeParams());
    expect(block).toContain('[custom_quiz]');
    expect(block).toContain('/app/quiz');
  });

  it('shows "Recommended:" section header', () => {
    const block = buildActiveWeekBlock(makeParams());
    expect(block).toContain('Recommended:');
  });
});

// ---------------------------------------------------------------------------
// Gate status
// ---------------------------------------------------------------------------

describe('buildActiveWeekBlock — gate status', () => {
  it('shows "passed ✓" when gate is passed', () => {
    const spec = makeSpec({ gate: { due_at: '2026-07-31T00:00:00Z', passed: true } });
    const block = buildActiveWeekBlock(makeParams({ spec }));
    expect(block).toContain('passed ✓');
  });

  it('shows due date when gate is pending', () => {
    const spec = makeSpec({ gate: { due_at: '2026-07-31T00:00:00Z', passed: false } });
    const block = buildActiveWeekBlock(makeParams({ spec }));
    expect(block).toContain('due:2026-07-31');
  });

  it('shows "no-gate" when there is no gate', () => {
    const spec = makeSpec({ gate: { due_at: null, passed: false } });
    const block = buildActiveWeekBlock(makeParams({ spec }));
    expect(block).toContain('no-gate');
  });
});

// ---------------------------------------------------------------------------
// Drills and reviews
// ---------------------------------------------------------------------------

describe('buildActiveWeekBlock — drills and reviews', () => {
  it('shows weak drill atoms with mastery %', () => {
    const spec = makeSpec({
      drills: [
        {
          atom: 'chain_rule_apply',
          mastery: 0.2,
          concept_id: 'derivatives_intro',
          concept_name: 'derivatives intro',
          concept_name_he: null,
        },
      ],
    });
    const block = buildActiveWeekBlock(makeParams({ spec }));
    expect(block).toContain('chain_rule_apply@20%');
  });

  it('shows "none" when no drills', () => {
    const block = buildActiveWeekBlock(makeParams());
    expect(block).toContain('Weak drills: none');
  });

  it('shows review count', () => {
    const spec = makeSpec({
      due_reviews: { count: 7, top_concepts: [] },
    });
    const block = buildActiveWeekBlock(makeParams({ spec }));
    expect(block).toContain('Reviews due: 7');
  });
});

// ---------------------------------------------------------------------------
// Plan health flags
// ---------------------------------------------------------------------------

describe('buildActiveWeekBlock — plan health', () => {
  it('shows needs_replan flag when active', () => {
    const block = buildActiveWeekBlock(
      makeParams({ planHealth: { needs_replan: true, overflow_count: 0 } }),
    );
    expect(block).toContain('needs_replan');
    expect(block).toContain('Health:');
  });

  it('shows overflow count when > 0', () => {
    const block = buildActiveWeekBlock(
      makeParams({ planHealth: { needs_replan: false, overflow_count: 3 } }),
    );
    expect(block).toContain('overflow: 3');
  });

  it('omits Health line when no flags', () => {
    const block = buildActiveWeekBlock(
      makeParams({ planHealth: { needs_replan: false, overflow_count: 0 } }),
    );
    expect(block).not.toContain('Health:');
  });
});

// ---------------------------------------------------------------------------
// Concept filtering
// ---------------------------------------------------------------------------

describe('buildActiveWeekBlock — concept filtering', () => {
  it('skips rest-kind concepts', () => {
    const params = makeParams({
      concepts: [
        makeConcept('derivatives_intro', { mastery: 0.45, name_he: 'נגזרת - מבוא' }),
        makeConcept('rest_day', { kind: 'rest' }),
      ],
    });
    const block = buildActiveWeekBlock(params);
    expect(block).not.toContain('[rest_day]');
    expect(block).toContain('[derivatives_intro]');
  });

  it('handles empty concepts gracefully', () => {
    const params = makeParams({ concepts: [] });
    const block = buildActiveWeekBlock(params);
    expect(block).toContain('## Active week');
    expect(block).not.toContain('Concepts:');
  });
});

// ---------------------------------------------------------------------------
// Size constraint
// ---------------------------------------------------------------------------

describe('buildActiveWeekBlock — size constraint', () => {
  it('stays ≤900 chars for a typical 4-concept week with 4 recommended actions', () => {
    const spec = makeSpec({
      gate: { due_at: '2026-07-31T00:00:00Z', passed: false },
      drills: [
        { atom: 'chain_rule_apply', mastery: 0.2, concept_id: 'derivatives_intro', concept_name: 'derivatives intro', concept_name_he: null },
        { atom: 'product_rule_apply', mastery: 0.35, concept_id: 'derivatives_intro', concept_name: 'derivatives intro', concept_name_he: null },
      ],
      due_reviews: { count: 5, top_concepts: [{ concept_id: 'limits', concept_name: 'Limits', concept_name_he: 'גבולות' }] },
      recommended: [
        { kind: 'quiz_gate', label_he: 'מבחן שבועי', label_en: 'Weekly gate quiz', href: '/quiz/week-1?plan_id=plan-abc&week_num=3', reason_he: 'גמור את המבחן', reason_en: 'Complete the gate' },
        { kind: 'drill', label_he: 'תרגול ממוקד בחולשות', label_en: 'Drill weak spots', href: '/app/practice?topics=derivatives_intro', reason_he: 'מתחת ל-60%', reason_en: 'below 60%' },
        { kind: 'review', label_he: '5 פריטים לחזרה', label_en: '5 items due for review', href: '/app/practice?topics=limits&mode=due', reason_he: 'חזרה מרווחת', reason_en: 'Spaced review' },
        { kind: 'custom_quiz', label_he: 'חידון על נושאי השבוע', label_en: "Quiz on this week's topics", href: '/app/quiz?topics=derivatives_intro,limits', reason_he: 'בדוק את עצמך', reason_en: 'Test yourself' },
      ],
    });
    const params: ActiveWeekBlockParams = {
      weekNumber: 3,
      concepts: [
        makeConcept('derivatives_intro', { mastery: 0.45, name_he: 'נגזרת - מבוא' }),
        makeConcept('limits', { mastery: 0.72, name_he: 'גבולות' }),
        makeConcept('integral_intro', { mastery: 0.3, name_he: 'אינטגרל - מבוא' }),
        makeConcept('sequences', { mastery: 0.6, name_he: 'סדרות' }),
      ],
      spec,
      planHealth: { needs_replan: false, overflow_count: 0 },
    };
    const block = buildActiveWeekBlock(params);
    expect(block.length).toBeLessThanOrEqual(900);
  });

  it('hard-truncates at 900 chars even for very long inputs', () => {
    const veryLongConceptName = 'x'.repeat(200);
    const spec = makeSpec({
      recommended: Array.from({ length: 4 }, (_, i) => ({
        kind: 'drill' as const,
        label_he: `פעולה ${'ארוכה_מאוד'.repeat(5)}_${i}`,
        label_en: `action_${i}`,
        href: `/app/practice?topics=${'very_long_concept_id'.repeat(3)}_${i}`,
        reason_he: 'סיבה',
        reason_en: 'reason',
      })),
    });
    const params = makeParams({
      weekNumber: 99,
      concepts: Array.from({ length: 8 }, (_, i) =>
        makeConcept(`concept_${veryLongConceptName}_${i}`, { mastery: 0.1 }),
      ),
      spec,
      planHealth: { needs_replan: true, overflow_count: 12 },
    });
    const block = buildActiveWeekBlock(params);
    expect(block.length).toBeLessThanOrEqual(900);
  });
});
