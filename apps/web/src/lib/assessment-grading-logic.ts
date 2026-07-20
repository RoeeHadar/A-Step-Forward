/**
 * Pure helpers for feedback-first assessment grading (unit-testable, no I/O).
 * Keep this file free of `server-only` so client UI can share `gradingUiPhase`.
 */

export const GRADE_ITEM_MAX_RETRIES = 3;

export type FeedbackStatus = 'pending' | 'graded' | 'failed';

export interface FeedbackLike {
  status: FeedbackStatus;
  retries?: number;
  process_score?: number;
}

export function isOpenAssessmentKind(kind: string): boolean {
  return kind === 'open' || kind === 'derivation' || kind === 'extended';
}

/** Pick the next open item that still needs an LLM/process grade pass. */
export function selectNextOpenItemId(
  openIds: string[],
  feedback: Record<string, FeedbackLike | undefined>,
  maxRetries: number = GRADE_ITEM_MAX_RETRIES,
): string | null {
  for (const id of openIds) {
    const f = feedback[id];
    if (!f) return id;
    if (f.status === 'pending') return id;
    if (f.status === 'failed' && (f.retries ?? 0) < maxRetries) return id;
  }
  return null;
}

/** True when every open item is graded or permanently failed (no more retries). */
export function opensStillPending(
  openIds: string[],
  feedback: Record<string, FeedbackLike | undefined>,
  maxRetries: number = GRADE_ITEM_MAX_RETRIES,
): boolean {
  return selectNextOpenItemId(openIds, feedback, maxRetries) != null;
}

/**
 * Apply permanent-failure zeros and fill missing open scores before aggregate.
 * Mutates `scores` in place and returns it.
 */
export function applySettledOpenScores(
  openIds: string[],
  feedback: Record<string, FeedbackLike | undefined>,
  scores: Record<string, number>,
): Record<string, number> {
  for (const id of openIds) {
    if (feedback[id]?.status === 'failed') scores[id] = 0;
    if (scores[id] === undefined) scores[id] = feedback[id]?.process_score ?? 0;
  }
  return scores;
}

/**
 * UI phase for a submit/grade-next payload.
 * Score must never show while pending/grading; failed is distinct from reviewing.
 */
export function gradingUiPhase(input: {
  grading_status?: string | null;
  score?: number | null;
}): 'pending' | 'failed' | 'complete' {
  const status = input.grading_status ?? (input.score != null ? 'complete' : 'pending');
  if (status === 'failed') return 'failed';
  if (status === 'complete' && input.score != null) return 'complete';
  if (status === 'complete' && input.score == null) return 'failed';
  if (status === 'pending' || status === 'grading') return 'pending';
  return input.score != null ? 'complete' : 'pending';
}

/** Bound client poll loops so a stuck grader cannot hang the tab forever. */
export function maxGradeNextPolls(
  openTotal: number,
  maxRetries: number = GRADE_ITEM_MAX_RETRIES,
): number {
  const n = Math.max(0, openTotal);
  return Math.max(8, n * (maxRetries + 1) + 12);
}
