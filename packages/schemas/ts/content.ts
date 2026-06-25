import { z } from 'zod';

export const subjectSummarySchema = z.object({
  subject: z.string(),
  section_count: z.number().int().nonnegative(),
  sample_grade: z.string().nullable(),
});
export type SubjectSummary = z.infer<typeof subjectSummarySchema>;

export const subjectListSchema = z.array(subjectSummarySchema);

export const contentSectionSchema = z.object({
  subject: z.string(),
  grade: z.string().nullable(),
  title: z.string(),
  body_md: z.string(),
  page_start: z.number().int().nullable(),
  page_end: z.number().int().nullable(),
  chunk_index: z.number().int().nullable().optional(),
});
export type ContentSection = z.infer<typeof contentSectionSchema>;

export const contentSectionsPageSchema = z.object({
  items: z.array(contentSectionSchema),
  total: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  page_size: z.number().int().positive(),
});
export type ContentSectionsPage = z.infer<typeof contentSectionsPageSchema>;

export const bagrutExamSchema = z.object({
  display_name: z.string(),
  file_url: z.string(),
  year: z.number().int().nullable(),
  exam_type: z.string(),
});
export type BagrutExam = z.infer<typeof bagrutExamSchema>;

export const bagrutExamListSchema = z.array(bagrutExamSchema);
