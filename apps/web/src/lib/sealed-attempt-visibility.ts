/**
 * Pure sealed-release helpers (no I/O).
 * Student-visible score/feedback only when grading_status is released (`complete`).
 */
export type SealedGradingStatus =
  | 'pending'
  | 'grading'
  | 'needs_human'
  | 'complete'
  | 'failed'
  | 'reopened';

/** True when the learner may see score, keys, and per-item feedback. */
export function isAttemptReleased(status: string | null | undefined): boolean {
  return status === 'complete';
}

/** Attempt still in the grader queue or waiting on a human. */
export function isAttemptSealed(status: string | null | undefined): boolean {
  return (
    status === 'pending' ||
    status === 'grading' ||
    status === 'needs_human' ||
    status === 'reopened' ||
    status === 'failed'
  );
}

export function gradingUiPhaseSealed(input: {
  grading_status?: string | null;
  score?: number | null;
}): 'pending' | 'failed' | 'needs_human' | 'complete' {
  const status =
    input.grading_status ?? (input.score != null ? 'complete' : 'pending');
  if (status === 'needs_human') return 'needs_human';
  if (status === 'failed') return 'failed';
  if (status === 'complete' && input.score != null) return 'complete';
  if (status === 'complete' && input.score == null) return 'failed';
  if (
    status === 'pending' ||
    status === 'grading' ||
    status === 'reopened'
  ) {
    return 'pending';
  }
  return input.score != null ? 'complete' : 'pending';
}

/** Strip marks/feedback from a grading view until release. Progress counts stay. */
export function sealGradingViewForClient<
  T extends {
    grading_status: string;
    score: number | null;
    passed: boolean | null;
    per_topic: Record<string, number>;
    weak_concepts: string[];
    item_feedback: Record<string, unknown>;
    item_scores: Record<string, number>;
  },
>(view: T): T {
  if (isAttemptReleased(view.grading_status)) return view;
  return {
    ...view,
    score: null,
    passed: null,
    per_topic: {},
    weak_concepts: [],
    item_feedback: {},
    item_scores: {},
  };
}

/**
 * When every open item is settled, decide release vs needs_human.
 * Any permanently failed open → needs_human (fail-closed, no fake score).
 */
export function settleOpenOutcome(
  openIds: string[],
  feedback: Record<string, { status?: string; retries?: number } | undefined>,
  maxRetries: number,
): 'release' | 'needs_human' | 'still_pending' {
  for (const id of openIds) {
    const f = feedback[id];
    if (!f) return 'still_pending';
    if (f.status === 'pending') return 'still_pending';
    if (f.status === 'failed' && (f.retries ?? 0) < maxRetries) return 'still_pending';
  }
  for (const id of openIds) {
    const f = feedback[id];
    if (f?.status === 'failed') return 'needs_human';
  }
  return 'release';
}
