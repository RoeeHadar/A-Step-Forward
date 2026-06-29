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
}

export interface MockExamStartResponse {
  exam_id: number;
  questions: ClientMockExamQuestion[];
  duration_minutes: number;
}
