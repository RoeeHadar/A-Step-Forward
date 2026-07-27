import { z } from 'zod';

export interface PlanConcept {
  concept_id: string;
  name: string;
  name_he: string | null;
  subject: string;
  mastery: number | null;
  suggested_sections: Array<{
    id: string;
    title: string;
    chunk_index: number | null;
    page_start: number | null;
  }>;
  recommended_bagrut: Array<{
    display_name: string;
    file_url: string;
    year: number | null;
    exam_type: string | null;
  }>;
  kind?: 'lesson' | 'train' | 'rest';
  target_count?: number | null;
}

export interface PlanWeek {
  id: string;
  plan_id: string;
  week_number: number;
  concepts: PlanConcept[];
  quiz_due_at: string | null;
  status: string;
}

export interface LearningPlan {
  id: string;
  learner_id: string;
  goal: string;
  start_date: string;
  end_date: string | null;
  status: string;
  weeks: PlanWeek[];
  goal_key?: string | null;
  needs_replan?: boolean;
  overflow_concepts?: string[] | null;
  pacing?: PlanPacing | null;
  plan_adjustment_kind?: string | null;
}

export interface PlanPacing {
  status: string;
  goal_readiness: number;
  weeks_left: number;
  remaining_scope: number;
  readiness?: number;
  critical_coverage?: number;
  exam_ready?: boolean;
  mock_passed?: boolean;
  readiness_message_key?: string;
}

export const planConceptSchema = z.object({}).passthrough() as unknown as z.ZodType<PlanConcept>;
export const planWeekSchema = z.object({}).passthrough() as unknown as z.ZodType<PlanWeek>;
export const learningPlanSchema: z.ZodType<LearningPlan> = z
  .object({ weeks: z.array(planWeekSchema).default([]) })
  .passthrough() as unknown as z.ZodType<LearningPlan>;

export interface QuizOption {
  key: string;
  text: string;
}

export interface QuizPart {
  label: string;
  body: string;
  points?: number;
}

export interface QuizQuestion {
  id: string;
  stem: string;
  topic: string;
  kind?: string;
  options?: QuizOption[];
  parts?: QuizPart[];
  total_points?: number;
}

export interface QuizStartResponse {
  quiz_id: string;
  time_limit_s: number;
  questions: QuizQuestion[];
}

export interface QuizItemFeedback {
  item_id: string;
  status?: 'pending' | 'graded' | 'failed' | string;
  points_earned?: number;
  points_available?: number;
  strengths?: string;
  steps_present?: string;
  steps_skipped?: string;
  logic_feedback?: string;
  material_feedback?: string;
  next_fix?: string;
}

export interface QuizSubmitResponse {
  attempt_id?: string;
  score?: number | null;
  passed?: boolean;
  grading_status?: 'pending' | 'processing' | 'complete' | 'failed' | string;
  open_total?: number;
  graded_open?: number;
  busy?: boolean;
  message?: string;
  per_topic: Record<string, number>;
  item_feedback?: Record<string, QuizItemFeedback>;
  plan_adapted?: boolean;
  next_week_concepts?: string[];
  weak_concepts: string[];
}

export const quizSubmitResponseSchema = z.object({}).passthrough() as unknown as z.ZodType<QuizSubmitResponse>;
