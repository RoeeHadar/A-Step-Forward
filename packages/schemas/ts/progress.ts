import { z } from 'zod';

export interface LearnerProgressConcept {
  concept_id: string;
  concept_name: string;
  concept_name_he?: string | null;
  current_score: number;
}

export interface LearnerProgress {
  concepts: LearnerProgressConcept[];
  streak_days: number;
  lessons_completed: number;
}

export const learnerProgressSchema = z.object({}).passthrough() as unknown as z.ZodType<LearnerProgress>;
export const educatorDashboardSchema = z.object({}).passthrough();

export type EducatorDashboard = z.infer<typeof educatorDashboardSchema>;
export interface AdminStats {
  total_learners: number;
  total_educators: number;
  active_sessions_24h: number;
  memory_writes_24h: number;
  avg_latency_ms: number;
}
