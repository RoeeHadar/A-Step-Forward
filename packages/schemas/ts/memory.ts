import { z } from 'zod';
import { citationSchema, confidenceScore, idStr, provenanceSchema } from './common';

export const memoryTypeSchema = z.enum([
  'working',
  'episodic',
  'semantic',
  'procedural',
  'affective',
  'context',
  'reflective',
  'source',
]);
export type MemoryType = z.infer<typeof memoryTypeSchema>;

export const memoryRecordSchema = z.object({
  id: idStr,
  learner_id: idStr,
  type: memoryTypeSchema,
  content: z.string(),
  summary: z.string().nullable().optional(),
  tags: z.array(z.string()).default([]),
  salience: confidenceScore.default(0.5),
  confidence: confidenceScore.default(0.5),
  valence: z.number().min(-1).max(1).default(0),
  decay_tau_days: z.number().default(14),
  last_accessed_at: z.string().datetime().optional(),
  access_count: z.number().default(0),
  superseded_by: idStr.nullable().optional(),
  superseded_at: z.string().datetime().nullable().optional(),
  provenance: provenanceSchema,
  kg_node_ids: z.array(idStr).default([]),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
  archived_at: z.string().datetime().nullable().optional(),
  deleted_at: z.string().datetime().nullable().optional(),
  expires_at: z.string().datetime().nullable().optional(),
});
export type MemoryRecord = z.infer<typeof memoryRecordSchema>;

export const memorySearchInputSchema = z.object({
  learner_id: idStr,
  query: z.string().min(1).max(2000),
  types: z.array(memoryTypeSchema).nullable().optional(),
  k: z.number().min(1).max(200).default(10),
  agent_id: z.string(),
  include_archived: z.boolean().default(false),
  min_strength: confidenceScore.default(0),
});
export type MemorySearchInput = z.infer<typeof memorySearchInputSchema>;

export const memorySearchResultSchema = z.object({
  record: memoryRecordSchema,
  score: confidenceScore,
  components: z.record(z.number()).default({}),
  citation: citationSchema.nullable().optional(),
});
export type MemorySearchResult = z.infer<typeof memorySearchResultSchema>;

export const memoryUpdateInputSchema = z.object({
  content: z.string().nullable().optional(),
  summary: z.string().nullable().optional(),
  tags: z.array(z.string()).nullable().optional(),
  salience: confidenceScore.nullable().optional(),
  confidence: confidenceScore.nullable().optional(),
  reason: z.string().min(1).max(500),
});
export type MemoryUpdateInput = z.infer<typeof memoryUpdateInputSchema>;

export const memoryTimelineSchema = z.array(memoryRecordSchema);
