import { z } from 'zod';

export const planConceptSchema = z.object({}).passthrough();
export const planWeekSchema = z.object({}).passthrough();
export const learningPlanSchema = z.object({}).passthrough();

export type PlanConcept = z.infer<typeof planConceptSchema>;
export type PlanWeek = z.infer<typeof planWeekSchema>;
export type LearningPlan = z.infer<typeof learningPlanSchema>;
export type QuizQuestion = Record<string, unknown>;
export type QuizStartResponse = Record<string, unknown>;
export type QuizSubmitResponse = Record<string, unknown>;
