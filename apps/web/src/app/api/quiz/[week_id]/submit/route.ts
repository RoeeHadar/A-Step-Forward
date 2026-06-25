import { auth } from '@clerk/nextjs/server';
import { API_BASE_URL } from '@/lib/api';

export const runtime = 'nodejs';

export async function POST(
  req: Request,
  { params }: { params: Promise<{ week_id: string }> },
) {
  const { userId, getToken } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  await params; // week_id unused — plan_id + week_num come from the body
  const body = (await req.json()) as {
    plan_id: string;
    week_num: number;
    answers: { item_id: string; chosen: string; time_spent_s: number | null }[];
    token: string;
  };

  const token = body.token || (await getToken());
  if (!token) return new Response('Unauthorized', { status: 401 });

  try {
    const res = await fetch(
      `${API_BASE_URL}/v1/learners/me/plans/${body.plan_id}/weeks/${body.week_num}/quiz/submit`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers: body.answers }),
      },
    );

    if (!res.ok) {
      const text = await res.text();
      return new Response(text, { status: res.status });
    }

    const data = await res.json();
    return Response.json(data);
  } catch (err) {
    return new Response(String(err), { status: 502 });
  }
}
