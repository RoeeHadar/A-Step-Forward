import { auth } from '@clerk/nextjs/server';
import { markAtomPracticed } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  if (!body || typeof body !== 'object') {
    return Response.json({ error: 'Body must be a JSON object' }, { status: 400 });
  }

  const b = body as Record<string, unknown>;
  const atomId = typeof b.atomId === 'string' ? b.atomId.trim() : '';
  const score = Number(b.score);

  if (!atomId) {
    return Response.json({ error: 'atomId is required' }, { status: 400 });
  }
  if (!Number.isFinite(score) || score < 0 || score > 1) {
    return Response.json({ error: 'score must be a number between 0 and 1' }, { status: 400 });
  }

  await markAtomPracticed(userId, atomId, score);
  return Response.json({ ok: true });
}