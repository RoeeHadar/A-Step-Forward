import { z } from 'zod';

export const learnerProgressSchema = z.object({}).passthrough();
export const educatorDashboardSchema = z.object({}).passthrough();

export type LearnerProgress = z.infer<typeof learnerProgressSchema>;
export type EducatorDashboard = z.infer<typeof educatorDashboardSchema>;
export type AdminStats = Record<string, unknown>;
