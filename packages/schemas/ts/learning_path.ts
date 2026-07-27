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
  pacing?: Record<string, unknown> | null;
  plan_adjustment_kind?: string | null;
}

export const planConceptSchema: z.ZodType<PlanConcept> = z.object({}).passthrough();
export const planWeekSchema: z.ZodType<PlanWeek> = z.object({}).passthrough();
export const learningPlanSchema: z.ZodType<LearningPlan> = z
  .object({ weeks: z.array(planWeekSchema).default([]) })
  .passthrough() as z.ZodType<LearningPlan>;

export type QuizQuestion = Record<string, unknown>;
export type QuizStartResponse = Record<string, unknown>;
export type QuizSubmitResponse = Record<string, unknown>;
