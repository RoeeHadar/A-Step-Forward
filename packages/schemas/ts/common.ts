import { z } from 'zod';

export const idStr = z.string().min(1).max(128);
export type IDStr = z.infer<typeof idStr>;

export const confidenceScore = z.number().min(0).max(1);
export type ConfidenceScore = z.infer<typeof confidenceScore>;

export const provenanceSchema = z.object({
  kind: z.enum([
    'chat',
    'lesson',
    'assessment',
    'upload',
    'agent_reflection',
    'system',
    'import',
    'verification',
  ]),
  id: idStr.nullable().optional(),
  agent: z.string().nullable().optional(),
  model: z.string().nullable().optional(),
  model_version: z.string().nullable().optional(),
  ts: z.string().datetime().optional(),
});
export type Provenance = z.infer<typeof provenanceSchema>;

export const citationSchema = z.object({
  source_kind: z.enum(['memory', 'kg_node', 'kg_chunk', 'lesson', 'resource', 'web']),
  source_id: idStr,
  quote: z.string().nullable().optional(),
  score: confidenceScore.nullable().optional(),
});
export type Citation = z.infer<typeof citationSchema>;
