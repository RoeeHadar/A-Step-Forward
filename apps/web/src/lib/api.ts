/**
 * Typed HTTP client for the FastAPI gateway.
 */
import { z } from 'zod';

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export interface ApiAuthHeaders {
  learnerId: string;
  role?: string;
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit & { schema: z.ZodType<T>; auth?: ApiAuthHeaders },
): Promise<T> {
  const headers: Record<string, string> = {
    'content-type': 'application/json',
    ...(init.headers as Record<string, string> | undefined),
  };

  if (init.auth) {
    headers['X-Learner-Id'] = init.auth.learnerId;
    if (init.auth.role) headers['X-Role'] = init.auth.role;
  }

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers,
    cache: init.cache ?? 'no-store',
  });

  if (!res.ok) {
    throw new Error(`API ${res.status} ${res.statusText} on ${path}`);
  }

  const json: unknown = await res.json();
  return init.schema.parse(json);
}

export async function apiFetchOptional<T>(
  path: string,
  init: RequestInit & { schema: z.ZodType<T>; auth?: ApiAuthHeaders },
): Promise<T | null> {
  try {
    return await apiFetch(path, init);
  } catch {
    return null;
  }
}

export { BASE as API_BASE_URL };
