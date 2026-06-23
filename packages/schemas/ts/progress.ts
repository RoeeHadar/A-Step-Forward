import { z } from 'zod';
import { idStr } from './common';

export const masteryPointSchema = z.object({
  date: z.string(),
  score: z.number().min(0).max(1),
});

export const conceptProgressSchema = z.object({
  concept_id: idStr,
  concept_name: z.string(),
  current_score: z.number().min(0).max(1),
  history: z.array(masteryPointSchema),
  next_review_at: z.string().datetime().nullable().optional(),
});

export const learnerProgressSchema = z.object({
  learner_id: idStr,
  concepts: z.array(conceptProgressSchema),
  streak_days: z.number(),
  total_minutes: z.number(),
  lessons_completed: z.number(),
});
export type LearnerProgress = z.infer<typeof learnerProgressSchema>;

export const educatorLearnerSummarySchema = z.object({
  learner_id: idStr,
  display_name: z.string(),
  avg_mastery: z.number().min(0).max(1),
  at_risk: z.boolean(),
  last_active_at: z.string().datetime().optional(),
});

export const educatorDashboardSchema = z.object({
  learners: z.array(educatorLearnerSummarySchema),
  class_avg_mastery: z.number().min(0).max(1),
  active_today: z.number(),
});
export type EducatorDashboard = z.infer<typeof educatorDashboardSchema>;

export const adminStatsSchema = z.object({
  total_learners: z.number(),
  total_educators: z.number(),
  active_sessions_24h: z.number(),
  memory_writes_24h: z.number(),
  avg_latency_ms: z.number(),
});
export type AdminStats = z.infer<typeof adminStatsSchema>;
