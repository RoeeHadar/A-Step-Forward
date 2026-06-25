import { API_BASE_URL } from '@/lib/api';
import { currentActiveWeek, learningPlanSchema, type LearningPlan } from '@/lib/learning-path-types';

async function planFetch(path: string, init?: RequestInit): Promise<LearningPlan> {
  const res = await fetch(`${API_BASE_URL}${path}`, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Plan API ${res.status}`);
  }
  const data: unknown = await res.json();
  return learningPlanSchema.parse(data);
}

export async function generateLearningPlan(token: string): Promise<LearningPlan> {
  return planFetch('/v1/learners/me/plans/generate', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function fetchCurrentPlan(token: string): Promise<LearningPlan | null> {
  const res = await fetch(`${API_BASE_URL}/v1/learners/me/plans/current`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: 'no-store',
  });
  if (res.status === 404) return null;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Plan API ${res.status}`);
  }
  const data: unknown = await res.json();
  return learningPlanSchema.parse(data);
}

export { currentActiveWeek };
