import { z } from 'zod';

export const memoryRecordSchema = z.object({}).passthrough();
export const memoryTimelineSchema = z.object({}).passthrough();

export type MemoryRecord = z.infer<typeof memoryRecordSchema>;
