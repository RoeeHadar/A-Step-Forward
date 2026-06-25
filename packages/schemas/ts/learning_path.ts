import { z } from 'zod';

export const contentSectionRefSchema = z.object({
  id: z.string(),
  title: z.string(),
  chunk_index: z.number().int().nullable().optional(),
  page_start: z.number().int().nullable().optional(),
});

export const bagrutRefSchema = z.object({
  display_name: z.string(),
  file_url: z.string(),
  year: z.number().int().nullable().optional(),
  exam_type: z.string().nullable().optional(),
});

export const planConceptSchema = z.object({
  concept_id: z.string(),
  name: z.string(),
  subject: z.string(),
  mastery: z.number().nullable().optional(),
  suggested_sections: z.array(contentSectionRefSchema).default([]),
  recommended_bagrut: z.array(bagrutRefSchema).default([]),
});

export const planWeekSchema = z.object({
  id: z.string(),
  plan_id: z.string(),
  week_number: z.number().int(),
  concepts: z.array(planConceptSchema).default([]),
  content_ids: z.array(z.string()).nullable().optional(),
  quiz_due_at: z.string().nullable().optional(),
  status: z.string(),
});

export const learningPlanSchema = z.object({
  id: z.string(),
  learner_id: z.string(),
  goal: z.string(),
  start_date: z.string(),
  end_date: z.string().nullable().optional(),
  status: z.string(),
  weeks: z.array(planWeekSchema).default([]),
});

export const quizOptionSchema = z.object({
  key: z.string(),
  text: z.string(),
});

export const quizQuestionSchema = z.object({
  id: z.string(),
  topic: z.string(),
  subject: z.string(),
  difficulty: z.number(),
  stem: z.string(),
  options: z.array(quizOptionSchema),
});

export const quizStartResponseSchema = z.object({
  quiz_id: z.string(),
  week_id: z.string(),
  plan_id: z.string(),
  week_number: z.number().int(),
  time_limit_s: z.number().int(),
  questions: z.array(quizQuestionSchema),
  started_at: z.string(),
});

export const quizSubmitResponseSchema = z.object({
  quiz_id: z.string(),
  score: z.number(),
  per_topic: z.record(z.string(), z.number()),
  weak_concepts: z.array(z.string()),
  plan_adapted: z.boolean(),
  next_week_concepts: z.array(z.string()).nullable().optional(),
});

export type PlanConcept = z.infer<typeof planConceptSchema>;
export type PlanWeek = z.infer<typeof planWeekSchema>;
export type LearningPlan = z.infer<typeof learningPlanSchema>;
export type QuizOption = z.infer<typeof quizOptionSchema>;
export type QuizQuestion = z.infer<typeof quizQuestionSchema>;
export type QuizStartResponse = z.infer<typeof quizStartResponseSchema>;
export type QuizSubmitResponse = z.infer<typeof quizSubmitResponseSchema>;
