import { auth } from '@clerk/nextjs/server';
import { API_BASE_URL } from '@/lib/api';

export const runtime = 'nodejs';

export async function POST(req: Request) {
  const { userId, getToken } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }

  const token = await getToken();
  const body = await req.json();

  const res = await fetch(`${API_BASE_URL}/v1/onboarding/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return Response.json(data, { status: res.status });
}

export async function GET() {
  const { userId, getToken } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }

  const token = await getToken();
  const res = await fetch(`${API_BASE_URL}/v1/onboarding/status`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  const data = await res.json();
  return Response.json(data, { status: res.status });
}
