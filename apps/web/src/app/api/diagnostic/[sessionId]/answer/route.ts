import { auth } from '@clerk/nextjs/server';
import { API_BASE_URL } from '@/lib/api';

export const runtime = 'nodejs';

export async function POST(
  req: Request,
  { params }: { params: Promise<{ sessionId: string }> },
) {
  const { userId, getToken } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }

  const { sessionId } = await params;
  const token = await getToken();
  const body = await req.json();

  const res = await fetch(`${API_BASE_URL}/v1/diagnostic/${sessionId}/answer`, {
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
