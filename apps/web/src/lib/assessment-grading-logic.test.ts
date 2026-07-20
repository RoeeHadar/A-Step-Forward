import { describe, expect, it, vi, beforeEach } from 'vitest';
import {
  applySettledOpenScores,
  gradingUiPhase,
  isOpenAssessmentKind,
  maxGradeNextPolls,
  opensStillPending,
  selectNextOpenItemId,
  GRADE_ITEM_MAX_RETRIES,
} from './assessment-grading-logic';
import { aggregateProcessScores, perTopicFromItemScores } from './process-grader';
import { evaluateGatePass } from './plan-pacing';
import { quizSubmitResponseSchema } from '../../../../packages/schemas/ts/learning_path';

describe('assessment-grading-logic: open kind detection', () => {
  it('treats open/derivation/extended as open', () => {
    expect(isOpenAssessmentKind('open')).toBe(true);
    expect(isOpenAssessmentKind('derivation')).toBe(true);
    expect(isOpenAssessmentKind('extended')).toBe(true);
  });

  it('treats closed kinds as not open', () => {
    expect(isOpenAssessmentKind('mcq')).toBe(false);
    expect(isOpenAssessmentKind('numeric')).toBe(false);
    expect(isOpenAssessmentKind('short_answer')).toBe(false);
    expect(isOpenAssessmentKind('true_false')).toBe(false);
  });
});

describe('assessment-grading-logic: next item + retries', () => {
  it('picks first pending open', () => {
    expect(
      selectNextOpenItemId(['a', 'b'], {
        a: { status: 'pending', retries: 0 },
        b: { status: 'pending', retries: 0 },
      }),
    ).toBe('a');
  });

  it('skips graded items', () => {
    expect(
      selectNextOpenItemId(['a', 'b'], {
        a: { status: 'graded', retries: 0, process_score: 0.8 },
        b: { status: 'pending', retries: 0 },
      }),
    ).toBe('b');
  });

  it('retries failed items below max retries', () => {
    expect(
      selectNextOpenItemId(['a'], {
        a: { status: 'failed', retries: GRADE_ITEM_MAX_RETRIES - 1 },
      }),
    ).toBe('a');
  });

  it('does not retry after max failures', () => {
    expect(
      selectNextOpenItemId(['a'], {
        a: { status: 'failed', retries: GRADE_ITEM_MAX_RETRIES },
      }),
    ).toBeNull();
  });

  it('opensStillPending is false when all graded or permanently failed', () => {
    expect(
      opensStillPending(['a', 'b'], {
        a: { status: 'graded', retries: 0, process_score: 1 },
        b: { status: 'failed', retries: GRADE_ITEM_MAX_RETRIES },
      }),
    ).toBe(false);
  });

  it('opensStillPending is true when something remains', () => {
    expect(
      opensStillPending(['a', 'b'], {
        a: { status: 'graded', retries: 0, process_score: 1 },
        b: { status: 'failed', retries: 1 },
      }),
    ).toBe(true);
  });
});

describe('assessment-grading-logic: settle scores', () => {
  it('zeros permanently failed opens and fills missing from process_score', () => {
    const scores: Record<string, number> = { closed1: 1 };
    applySettledOpenScores(
      ['o1', 'o2', 'o3'],
      {
        o1: { status: 'graded', process_score: 0.5 },
        o2: { status: 'failed', retries: 3 },
        o3: { status: 'graded', process_score: 0.25 },
      },
      scores,
    );
    expect(scores).toEqual({ closed1: 1, o1: 0.5, o2: 0, o3: 0.25 });
  });

  it('does not invent headline score before settle — missing open → 0', () => {
    const scores: Record<string, number> = {};
    applySettledOpenScores(['missing'], {}, scores);
    expect(scores.missing).toBe(0);
  });
});

describe('assessment-grading-logic: UI phase', () => {
  it('pending while grading_status pending even if score accidentally set', () => {
    // Server should never send score while pending; UI still must not treat as complete.
    expect(gradingUiPhase({ grading_status: 'pending', score: 1 })).toBe('pending');
    expect(gradingUiPhase({ grading_status: 'grading', score: null })).toBe('pending');
  });

  it('failed wins over null score (no infinite reviewing)', () => {
    expect(gradingUiPhase({ grading_status: 'failed', score: null })).toBe('failed');
  });

  it('complete only when status complete AND score present', () => {
    expect(gradingUiPhase({ grading_status: 'complete', score: 0 })).toBe('complete');
    expect(gradingUiPhase({ grading_status: 'complete', score: 0.9 })).toBe('complete');
    expect(gradingUiPhase({ grading_status: 'complete', score: null })).toBe('failed');
  });

  it('legacy payload with score and no status → complete', () => {
    expect(gradingUiPhase({ score: 0.8 })).toBe('complete');
  });

  it('legacy payload with neither → pending (never invent)', () => {
    expect(gradingUiPhase({})).toBe('pending');
  });
});

describe('assessment-grading-logic: poll bound', () => {
  it('scales with open count and has a floor', () => {
    expect(maxGradeNextPolls(0)).toBeGreaterThanOrEqual(8);
    expect(maxGradeNextPolls(4)).toBeGreaterThan(maxGradeNextPolls(1));
  });
});

describe('feedback-first gate math', () => {
  it('mixed closed+open: high closed cannot hide weak open process', () => {
    const ids = ['c1', 'c2', 'o1', 'o2'];
    const scores = { c1: 1, c2: 1, o1: 0.2, o2: 0.2 };
    const aggregate = aggregateProcessScores(ids, scores);
    expect(aggregate).toBe(0.6);
    // Below 0.75 gate bar
    const gate = evaluateGatePass({
      aggregateScore: aggregate,
      perTopic: perTopicFromItemScores(
        [
          { id: 'c1', topic: 'easy' },
          { id: 'c2', topic: 'easy' },
          { id: 'o1', topic: 'hard_open' },
          { id: 'o2', topic: 'hard_open' },
        ],
        scores,
      ),
      goalKey: null,
      passThreshold: 0.75,
    });
    expect(gate.passed).toBe(false);
  });

  it('process-perfect opens at threshold pass aggregate bar', () => {
    const ids = ['o1', 'o2', 'o3', 'o4'];
    const scores = { o1: 0.75, o2: 0.75, o3: 0.75, o4: 0.75 };
    expect(aggregateProcessScores(ids, scores)).toBe(0.75);
    expect(
      evaluateGatePass({
        aggregateScore: 0.75,
        perTopic: {},
        goalKey: null,
        passThreshold: 0.75,
      }).passed,
    ).toBe(true);
  });

  it('all-empty opens settle to 0 and fail', () => {
    const scores = applySettledOpenScores(
      ['a', 'b'],
      {
        a: { status: 'graded', process_score: 0 },
        b: { status: 'graded', process_score: 0 },
      },
      {},
    );
    const agg = aggregateProcessScores(['a', 'b'], scores);
    expect(agg).toBe(0);
    expect(
      evaluateGatePass({
        aggregateScore: agg,
        perTopic: {},
        goalKey: null,
        passThreshold: 0.75,
      }).passed,
    ).toBe(false);
  });
});

describe('quizSubmitResponseSchema feedback-first', () => {
  it('accepts pending payload with null score', () => {
    const parsed = quizSubmitResponseSchema.safeParse({
      quiz_id: 'q1',
      score: null,
      per_topic: {},
      weak_concepts: [],
      plan_adapted: false,
      passed: null,
      attempt_id: 'att-1',
      grading_status: 'pending',
      open_pending: 2,
      open_total: 2,
      graded_open: 0,
      item_feedback: {
        o1: {
          item_id: 'o1',
          status: 'pending',
          retries: 0,
          strengths: '',
          steps_present: '',
          steps_skipped: '',
          logic: '',
          material_anchoring: '',
          points_earned: 0,
          points_available: 20,
          process_score: 0,
          next_fix: '',
        },
      },
    });
    expect(parsed.success).toBe(true);
  });

  it('rejects inventing a non-number score type', () => {
    const parsed = quizSubmitResponseSchema.safeParse({
      quiz_id: 'q1',
      score: '100%',
      per_topic: {},
      weak_concepts: [],
      plan_adapted: false,
    });
    expect(parsed.success).toBe(false);
  });

  it('accepts complete payload with score 0 (honest fail)', () => {
    const parsed = quizSubmitResponseSchema.safeParse({
      quiz_id: 'q1',
      score: 0,
      per_topic: { derivatives: 0 },
      weak_concepts: ['derivatives'],
      plan_adapted: false,
      passed: false,
      grading_status: 'complete',
    });
    expect(parsed.success).toBe(true);
  });
});

vi.mock('@/lib/llm-provider', () => ({
  llmCompleteJson: vi.fn(),
}));

describe('gradeOpenItemProcess (mocked LLM)', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('empty response → graded 0 without LLM', async () => {
    const { llmCompleteJson } = await import('@/lib/llm-provider');
    const { gradeOpenItemProcess } = await import('./process-grader');
    const out = await gradeOpenItemProcess({
      item_id: 'x',
      stem: 'Prove…',
      response: '   ',
      points_available: 20,
      locale: 'he',
    });
    expect(out.status).toBe('graded');
    expect(out.process_score).toBe(0);
    expect(out.points_earned).toBe(0);
    expect(llmCompleteJson).not.toHaveBeenCalled();
  });

  it('LLM failure → failed status with incremented retries (no invented score)', async () => {
    const { llmCompleteJson } = await import('@/lib/llm-provider');
    vi.mocked(llmCompleteJson).mockResolvedValueOnce({ json: null } as never);
    const { gradeOpenItemProcess } = await import('./process-grader');
    const out = await gradeOpenItemProcess({
      item_id: 'x',
      stem: 'Prove…',
      response: 'final answer 42',
      prior_retries: 1,
      points_available: 20,
    });
    expect(out.status).toBe('failed');
    expect(out.retries).toBe(2);
    expect(out.process_score).toBe(0);
  });

  it('clamps points_earned and computes process_score', async () => {
    const { llmCompleteJson } = await import('@/lib/llm-provider');
    vi.mocked(llmCompleteJson).mockResolvedValueOnce({
      json: {
        strengths: 'ok',
        steps_present: 'step1',
        steps_skipped: 'step2',
        logic: 'fine',
        material_anchoring: 'yes',
        points_earned: 999,
        next_fix: 'none',
      },
    } as never);
    const { gradeOpenItemProcess } = await import('./process-grader');
    const out = await gradeOpenItemProcess({
      item_id: 'x',
      stem: 'Prove…',
      response: 'full worked solution with steps',
      points_available: 20,
    });
    expect(out.status).toBe('graded');
    expect(out.points_earned).toBe(20);
    expect(out.process_score).toBe(1);
  });

  it('partial credit is process-aware (not binary)', async () => {
    const { llmCompleteJson } = await import('@/lib/llm-provider');
    vi.mocked(llmCompleteJson).mockResolvedValueOnce({
      json: {
        strengths: 'started well',
        steps_present: 'definition',
        steps_skipped: 'conclusion',
        logic: 'gap',
        material_anchoring: 'partial',
        points_earned: 10,
        next_fix: 'finish the proof',
      },
    } as never);
    const { gradeOpenItemProcess } = await import('./process-grader');
    const out = await gradeOpenItemProcess({
      item_id: 'x',
      stem: 'Prove…',
      response: 'I wrote the definition then jumped to QED',
      points_available: 20,
    });
    expect(out.process_score).toBe(0.5);
    expect(out.next_fix).toContain('finish');
  });
});
