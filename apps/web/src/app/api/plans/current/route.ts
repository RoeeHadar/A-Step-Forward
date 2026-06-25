import { auth } from '@clerk/nextjs/server';
import { API_BASE_URL } from '@/lib/api';

export const runtime = 'nodejs';

export async function GET() {
  const { userId, getToken } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }

  const token = await getToken();
  const res = await fetch(`${API_BASE_URL}/v1/learners/me/plans/current`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: 'no-store',
  });

  const data = await res.json().catch(() => ({}));
  return Response.json(data, { status: res.status });
}
