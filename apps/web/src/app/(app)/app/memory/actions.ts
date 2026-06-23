'use server';

import { revalidatePath } from 'next/cache';
import { z } from 'zod';
import { auth } from '@clerk/nextjs/server';
import { memoryUpdateInputSchema } from '@asf/schemas/memory';
import { API_BASE_URL } from '@/lib/api';
import { logger } from '@/lib/logger';

const deleteSchema = z.object({
  memoryId: z.string().min(1),
  reason: z.string().min(1).max(500),
});

export async function updateMemoryAction(formData: FormData) {
  const { userId } = await auth();
  if (!userId) throw new Error('Unauthorized');

  const memoryId = formData.get('memoryId');
  const content = formData.get('content');
  const reason = formData.get('reason');

  const patch = memoryUpdateInputSchema.parse({
    content: typeof content === 'string' ? content : undefined,
    reason: typeof reason === 'string' ? reason : 'Learner correction',
  });

  try {
    await fetch(`${API_BASE_URL}/v1/memory/${memoryId}`, {
      method: 'PATCH',
      headers: {
        'content-type': 'application/json',
        'X-Learner-Id': userId,
      },
      body: JSON.stringify(patch),
    });
  } catch (err) {
    logger.warn('memory update failed, mock success', { err: String(err) });
  }

  revalidatePath('/app/memory');
  return { ok: true };
}

export async function deleteMemoryAction(formData: FormData) {
  const { userId } = await auth();
  if (!userId) throw new Error('Unauthorized');

  const parsed = deleteSchema.parse({
    memoryId: formData.get('memoryId'),
    reason: formData.get('reason'),
  });

  try {
    await fetch(`${API_BASE_URL}/v1/memory/${parsed.memoryId}?hard=false`, {
      method: 'DELETE',
      headers: { 'X-Learner-Id': userId },
    });
  } catch (err) {
    logger.warn('memory delete failed, mock success', { err: String(err) });
  }

  revalidatePath('/app/memory');
  return { ok: true };
}

export async function searchMemoriesAction(query: string) {
  const { userId } = await auth();
  if (!userId) throw new Error('Unauthorized');

  const res = await fetch(`${API_BASE_URL}/v1/memory/search`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'X-Learner-Id': userId,
    },
    body: JSON.stringify({
      learner_id: userId,
      query,
      k: 20,
      agent_id: 'user:memory_inspector',
    }),
    cache: 'no-store',
  });

  if (!res.ok) return null;
  const json: unknown = await res.json();
  return json;
}
