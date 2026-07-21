export type MockExamQuestionKind = 'mcq' | 'short_answer' | 'extended';

export interface ClientMockExamQuestion {
  id: string;
  number: number;
  kind: MockExamQuestionKind;
  points: number;
  stem_he: string;
  stem_en: string;
  options?: Array<{ key: string; text_he: string; text_en: string }>;
}

export interface MockExamSubmitFeedback {
  question_id: string;
  correct: boolean | null;
  chosen?: string;
  correct_answer?: string;
  explanation_he?: string;
  explanation_en?: string;
}

export interface MockExamSubmitResponse {
  score_mcq: number;
  max_mcq: number;
  feedback_by_question: MockExamSubmitFeedback[];
  attempt_id?: string | null;
  grading_status?: 'pending' | 'grading' | 'needs_human' | 'complete' | 'failed' | 'reopened';
  /** Overall process-aware score; null until grading complete */
  score?: number | null;
  passed?: boolean | null;
  item_feedback?: Record<string, unknown>;
  open_pending?: number;
  open_total?: number;
  graded_open?: number;
}

export interface MockExamStartResponse {
  exam_id: number;
  questions: ClientMockExamQuestion[];
  duration_minutes: number;
}
