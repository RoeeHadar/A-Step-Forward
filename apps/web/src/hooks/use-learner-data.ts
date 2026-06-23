'use client';

import { useQuery } from '@tanstack/react-query';
import { learnerDashboardSchema } from '@asf/schemas/curriculum';
import { learnerProgressSchema } from '@asf/schemas/progress';
import { memoryTimelineSchema } from '@asf/schemas/memory';
import { z } from 'zod';

async function fetchJson<T>(path: string, schema: z.ZodType<T>): Promise<T> {
  const res = await fetch(path, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch ${path}`);
  const json: unknown = await res.json();
  return schema.parse(json);
}

export function useDashboardQuery(enabled = true) {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: () => fetchJson('/api/dashboard', learnerDashboardSchema),
    enabled,
  });
}

export function useProgressQuery(enabled = true) {
  return useQuery({
    queryKey: ['progress'],
    queryFn: () => fetchJson('/api/progress', learnerProgressSchema),
    enabled,
  });
}

export function useMemoriesQuery(enabled = true) {
  return useQuery({
    queryKey: ['memories'],
    queryFn: () => fetchJson('/api/memory', memoryTimelineSchema),
    enabled,
  });
}
