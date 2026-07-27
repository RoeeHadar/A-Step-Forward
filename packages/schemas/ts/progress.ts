import { z } from 'zod';

export const learnerProgressSchema = z.object({}).passthrough();
export const educatorDashboardSchema = z.object({}).passthrough();

export type LearnerProgress = z.infer<typeof learnerProgressSchema>;
export type EducatorDashboard = z.infer<typeof educatorDashboardSchema>;
export interface AdminStats {
  total_learners: number;
  total_educators: number;
  active_sessions_24h: number;
  memory_writes_24h: number;
  avg_latency_ms: number;
}
