import { z } from 'zod';

export interface LessonObjective {
  id: string;
  statement: string;
}

export interface Lesson {
  id: string;
  title: string;
  modality: string;
  est_minutes: number;
  body_md: string;
  objectives: LessonObjective[];
}

export const lessonSchema: z.ZodType<Lesson> = z
  .object({
    id: z.string().default(''),
    title: z.string().default(''),
    modality: z.string().default('lesson'),
    est_minutes: z.number().default(0),
    body_md: z.string().default(''),
    objectives: z
      .array(z.object({ id: z.string().default(''), statement: z.string().default('') }))
      .default([]),
  })
  .passthrough() as z.ZodType<Lesson>;
export const learnerDashboardSchema = z.object({}).passthrough();

export type LearnerDashboard = z.infer<typeof learnerDashboardSchema>;
