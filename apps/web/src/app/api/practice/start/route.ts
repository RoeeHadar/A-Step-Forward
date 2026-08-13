/**
 * POST /api/practice/start — create a practice session and first sealed item.
 * Requires topic_ids (multi-select). Remembers last topics on the learner profile.
 */
import { auth } from '@clerk/nextjs/server';
import { advancePracticeItem } from '@/lib/practice-queue';
import { parsePracticeQueueMode } from '@/lib/practice-arena';
import { parsePracticeTopicIds } from '@/lib/practice-topics';
import {
  createPracticeSession,
  markPracticeFingerprintSeen,
  toPracticeSessionPublic,
  updatePracticeSession,
} from '@/lib/practice-session';
import { getLearnerProfile } from '@/lib/neon-db';
import { neon, neonConfig } from '@neondatabase/serverless';

neonConfig.fetchConnectionCache = true;
const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function rememberPracticeTopics(learnerId: string, topicIds: string[]) {
  if (!sql || !topicIds.length) return;
  try {
    const profile = await getLearnerProfile(learnerId).catch(() => null);
    const existing = { ...(profile?.personality_profile ?? {}) } as Record<string, unknown>;
    existing.last_practice_topic_ids = topicIds;
    await sql`
      UPDATE learner_profiles
      SET personality_profile = ${JSON.stringify(existing)}::jsonb, updated_at = NOW()
      WHERE learner_id = ${learnerId}
    `;
  } catch {
    // non-fatal
  }
}

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
  const topicIds = parsePracticeTopicIds(body.topic_ids);
  const queueMode = parsePracticeQueueMode(body.queue_mode ?? body.mode);
  if (!topicIds.length && !conceptFilter && queueMode === 'default') {
    return Response.json(
      {
        error: 'topics_required',
        message: 'Select at least one practice topic before starting.',
      },
      { status: 400 },
    );
  }

  const goalItems =
    typeof body.goal_items === 'number' ? body.goal_items : undefined;
  const goalMinutes =
    typeof body.goal_minutes === 'number' ? body.goal_minutes : undefined;

  const session = await createPracticeSession({
    learnerId: userId,
    conceptFilter,
    topicIds,
    goalItems,
    goalMinutes,
    queueMode,
  });
  if (!session) {
    return Response.json({ error: 'session_create_failed' }, { status: 503 });
  }

  void rememberPracticeTopics(userId, topicIds);

  const advanced = await advancePracticeItem({
    learnerId: userId,
    conceptFilter: session.concept_filter,
    topicIds: session.topic_ids,
    queueMode: session.queue_mode,
    seenIds: session.seen_ids,
    recentCorrect: session.recent_correct,
    generatedCount: session.generated_count,
  });

  if (!advanced || 'thin_topic' in advanced) {
    // End orphan empty session so history stays clean.
    await updatePracticeSession(
      userId,
      session.id,
      { status: 'ended', current_graded: true },
      session.version,
    ).catch(() => null);
    return Response.json(
      {
        error: 'thin_topic',
        message:
          'Not enough quality exam-style items for these topics yet. Try another topic or check back soon.',
        focus_concept_id:
          advanced && 'focusConceptId' in advanced ? advanced.focusConceptId : null,
      },
      { status: 503 },
    );
  }

  const seen = [...session.seen_ids];
  if (advanced.item.question_id) seen.push(advanced.item.question_id);
  seen.push(advanced.item.id);

  const updated = await updatePracticeSession(
    userId,
    session.id,
    {
      current_item: advanced.item,
      hint_step: 0,
      current_graded: false,
      focus_concept_id: advanced.focusConceptId,
      seen_ids: seen,
      generated_count:
        advanced.item.source === 'generated'
          ? session.generated_count + 1
          : session.generated_count,
    },
    session.version,
  );
  if (!updated) {
    return Response.json({ error: 'session_conflict' }, { status: 409 });
  }

  // Only burn the fingerprint after the learner actually received the item.
  await markPracticeFingerprintSeen({
    learnerId: userId,
    fingerprint: advanced.item.fingerprint,
    conceptId: advanced.item.concept_id,
  });

  return Response.json(toPracticeSessionPublic(updated));
}
