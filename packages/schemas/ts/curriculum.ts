import { z } from 'zod';
import { idStr } from './common';

export const levelSchema = z.enum(['beginner', 'intermediate', 'advanced']);
export const modalitySchema = z.enum(['reading', 'interactive', 'video', 'project', 'discussion']);
export const bloomsLevelSchema = z.enum([
  'remember',
  'understand',
  'apply',
  'analyze',
  'evaluate',
  'create',
]);
export const questionTypeSchema = z.enum(['mcq', 'short', 'essay', 'code']);
export const assessmentTypeSchema = z.enum(['quiz', 'exercise', 'project']);
export const resourceKindSchema = z.enum(['article', 'video', 'book', 'interactive']);

export const conceptSchema = z.object({
  id: idStr,
  name: z.string().min(1).max(128),
  summary: z.string().optional(),
  prerequisites: z.array(idStr).default([]),
});
export type Concept = z.infer<typeof conceptSchema>;

export const resourceSchema = z.object({
  id: idStr,
  kind: resourceKindSchema,
  uri: z.string(),
  title: z.string(),
  summary: z.string(),
  license: z.string(),
  minutes: z.number().optional(),
});
export type Resource = z.infer<typeof resourceSchema>;

export const questionSchema = z.object({
  id: idStr,
  stem: z.string(),
  type: questionTypeSchema,
  choices: z.array(z.string()).optional(),
  answer: z.string().optional(),
  rubric: z.string().optional(),
  concepts: z.array(idStr).default([]),
});
export type Question = z.infer<typeof questionSchema>;

export const assessmentSchema = z.object({
  id: idStr,
  type: assessmentTypeSchema,
  title: z.string(),
  questions: z.array(questionSchema).default([]),
  rubric: z.string(),
  concepts: z.array(idStr).default([]),
});
export type Assessment = z.infer<typeof assessmentSchema>;

export const objectiveSchema = z.object({
  id: idStr,
  statement: z.string(),
  blooms_level: bloomsLevelSchema,
  concepts: z.array(idStr).min(1),
});

export const lessonSchema = z.object({
  id: idStr,
  title: z.string(),
  body_md: z.string(),
  modality: modalitySchema,
  objectives: z.array(objectiveSchema).min(2),
  concepts: z.array(idStr).default([]),
  resources: z.array(idStr).default([]),
  est_minutes: z.number().min(5).max(180).default(15),
});
export type Lesson = z.infer<typeof lessonSchema>;

export const unitSchema = z.object({
  id: idStr,
  title: z.string(),
  summary: z.string(),
  objectives: z.array(objectiveSchema).default([]),
  lessons: z.array(lessonSchema).default([]),
  assessments: z.array(assessmentSchema).default([]),
});
export type Unit = z.infer<typeof unitSchema>;

export const courseSchema = z.object({
  id: idStr,
  title: z.string(),
  level: levelSchema,
  summary: z.string(),
  prerequisites: z.array(idStr).default([]),
  units: z.array(unitSchema).min(1),
  resources: z.array(resourceSchema).default([]),
});
export type Course = z.infer<typeof courseSchema>;

export const courseSummarySchema = z.object({
  id: idStr,
  title: z.string(),
  level: levelSchema,
  summary: z.string(),
  unit_count: z.number().min(0),
  lesson_count: z.number().min(0),
});
export type CourseSummary = z.infer<typeof courseSummarySchema>;

export const dashboardLessonSchema = z.object({
  id: idStr,
  title: z.string(),
  progress: z.number().min(0).max(1),
  last_accessed_at: z.string().datetime().optional(),
  est_minutes: z.number(),
});
export type DashboardLesson = z.infer<typeof dashboardLessonSchema>;

export const learnerDashboardSchema = z.object({
  recent_lessons: z.array(dashboardLessonSchema),
  mastery_summary: z.array(
    z.object({
      concept_id: idStr,
      concept_name: z.string(),
      score: z.number().min(0).max(1),
    }),
  ),
});
export type LearnerDashboard = z.infer<typeof learnerDashboardSchema>;
