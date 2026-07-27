import { z } from 'zod';

export interface PlanConcept {
  [key: string]: unknown;
  concept_id?: string;
  mastery?: number | null;
}

export interface PlanWeek {
  [key: string]: unknown;
  id?: string;
  week_number?: number;
  status?: string;
  concepts?: PlanConcept[];
  quiz_due_at?: string | null;
}

export interface LearningPlan {
  [key: string]: unknown;
  weeks: PlanWeek[];
}

export const planConceptSchema: z.ZodType<PlanConcept> = z.object({}).passthrough();
export const planWeekSchema: z.ZodType<PlanWeek> = z.object({}).passthrough();
export const learningPlanSchema: z.ZodType<LearningPlan> = z
  .object({ weeks: z.array(planWeekSchema).default([]) })
  .passthrough() as z.ZodType<LearningPlan>;

export type QuizQuestion = Record<string, unknown>;
export type QuizStartResponse = Record<string, unknown>;
export type QuizSubmitResponse = Record<string, unknown>;
