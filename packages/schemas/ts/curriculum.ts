import { z } from 'zod';

export const lessonSchema = z.object({}).passthrough();
export const learnerDashboardSchema = z.object({}).passthrough();

export type Lesson = z.infer<typeof lessonSchema>;
export type LearnerDashboard = z.infer<typeof learnerDashboardSchema>;
