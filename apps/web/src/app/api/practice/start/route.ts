/**
 * POST /api/practice/start — create a practice session and first sealed item.
 */
import { auth } from '@clerk/nextjs/server';
import { advancePracticeItem } from '@/lib/practice-queue';
import {
  createPracticeSession,
  toPracticeSessionPublic,
  updatePracticeSession,
} from '@/lib/practice-session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: Record<string, unknown> = {};
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    body = {};
  }

  const conceptFilter =
    typeof body.concept_id === 'string' && body.concept_id.trim()
      ? body.concept_id.trim()
      : null;
  const goalItems =
    typeof body.goal_items === 'number' ? body.goal_items : undefined;
  const goalMinutes =
    typeof body.goal_minutes === 'number' ? body.goal_minutes : undefined;

  const session = await createPracticeSession({
    learnerId: userId,
    conceptFilter,
    goalItems,
    goalMinutes,
  });
  if (!session) {
    return Response.json({ error: 'session_create_failed' }, { status: 503 });
  }

  const advanced = await advancePracticeItem({
    learnerId: userId,
    conceptFilter: session.concept_filter,
    seenIds: session.seen_ids,
    recentCorrect: session.recent_correct,
    generatedCount: session.generated_count,
  });
  if (!advanced) {
    return Response.json(
      {
        error: 'no_items',
        message: 'No practice items available for your plan right now.',
      },
      { status: 503 },
    );
  }

  const seen = [...session.seen_ids];
  if (advanced.item.question_id) seen.push(advanced.item.question_id);
  seen.push(advanced.item.id);

  const updated = await updatePracticeSession(userId, session.id, {
    current_item: advanced.item,
    hint_step: 0,
    focus_concept_id: advanced.focusConceptId,
    seen_ids: seen,
    generated_count:
      advanced.item.source === 'generated'
        ? session.generated_count + 1
        : session.generated_count,
  });

  return Response.json(toPracticeSessionPublic(updated ?? session));
}
