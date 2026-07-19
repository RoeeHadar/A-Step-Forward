/**
 * TEMPORARY read-only self-diagnostic for the "Progress / Memory / My Tests not
 * updating" investigation.
 *
 * Returns row counts, latest timestamps, and — critically — how many of the
 * caller's own concept_mastery rows the subject-scope filter HIDES from the
 * Progress + Memory pages. Scoped to the logged-in caller only (their own
 * data), reads nothing else, writes nothing.
 *
 * DELETE THIS ROUTE once the diagnosis is captured.
 */
import { neon } from '@neondatabase/serverless';
import { getAuthContext } from '@/lib/auth';
import { getLearnerProfile } from '@/lib/neon-db';
import { conceptMatchesSubjects, resolveConceptSubject } from '@/lib/concept-scope';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type Row = Record<string, unknown>;

export async function GET() {
  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
  if (!url) return Response.json({ error: 'DATABASE_URL not set on this deployment' }, { status: 503 });

  const s = neon(url);
  const learnerId = ctx.learnerId;
  const num = (v: unknown): number => Number(v ?? 0);

  const profile = await getLearnerProfile(learnerId).catch(() => null);
  const subjects: string[] = Array.isArray(profile?.subjects) ? profile.subjects : [];
  const hasPersona = Boolean((profile as { learner_persona?: string } | null)?.learner_persona);

  // ---- concept_mastery + the scope-filter effect (hypothesis A) ----
  let mastery: Row = { _error: 'not run' };
  try {
    const rows = (await s`
      SELECT concept_id, score::float AS score, data_points, last_activity
      FROM concept_mastery WHERE learner_id = ${learnerId}
      ORDER BY last_activity DESC NULLS LAST
    `) as Array<{ concept_id: string; score: number; data_points: number; last_activity: string }>;

    let shown = 0;
    const hiddenSamples: Array<{ concept_id: string; resolved_subject: string | null; score: number }> = [];
    for (const r of rows) {
      if (conceptMatchesSubjects(r.concept_id, subjects)) {
        shown += 1;
      } else if (hiddenSamples.length < 15) {
        hiddenSamples.push({
          concept_id: r.concept_id,
          resolved_subject: resolveConceptSubject(r.concept_id),
          score: r.score,
        });
      }
    }
    mastery = {
      total_rows: rows.length,
      mastered_ge_0_7: rows.filter((r) => r.score >= 0.7).length,
      latest_activity: rows[0]?.last_activity ?? null,
      shown_after_scope_filter: shown,
      HIDDEN_by_scope_filter: rows.length - shown,
      hidden_samples: hiddenSamples,
      recent_sample: rows.slice(0, 10).map((r) => ({
        concept_id: r.concept_id,
        score: r.score,
        resolved_subject: resolveConceptSubject(r.concept_id),
        in_scope: conceptMatchesSubjects(r.concept_id, subjects),
        last_activity: r.last_activity,
      })),
    };
  } catch (err) {
    mastery = { _error: (err as Error)?.message ?? String(err) };
  }

  const wrap = async (fn: () => Promise<Row>): Promise<Row> => {
    try {
      return await fn();
    } catch (err) {
      return { _error: (err as Error)?.message ?? String(err) };
    }
  };

  const skillPractice = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(last_practiced) AS latest FROM skill_practice WHERE learner_id = ${learnerId}`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null };
  });

  const chatTurns = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(created_at) AS latest FROM chat_turns WHERE learner_id = ${learnerId}`) as Row[];
    const byAgent = (await s`SELECT agent AS key, COUNT(*)::int AS n FROM chat_turns WHERE learner_id = ${learnerId} GROUP BY agent ORDER BY agent`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null, by_agent: byAgent };
  });

  const agentNotes = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(created_at) AS latest FROM learner_agent_notes WHERE learner_id = ${learnerId}`) as Row[];
    const byAgent = (await s`SELECT agent AS key, COUNT(*)::int AS n FROM learner_agent_notes WHERE learner_id = ${learnerId} GROUP BY agent ORDER BY agent`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null, by_agent: byAgent };
  });

  const testAttempts = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(created_at) AS latest FROM test_attempts WHERE learner_id = ${learnerId}`) as Row[];
    const byKind = (await s`SELECT kind AS key, COUNT(*)::int AS n, MAX(created_at) AS latest FROM test_attempts WHERE learner_id = ${learnerId} GROUP BY kind ORDER BY kind`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null, by_kind: byKind };
  });

  const otherQuizzes = await wrap(async () => {
    const wk = (await s`SELECT COUNT(*)::int AS gen, COUNT(submitted_at)::int AS submitted FROM weekly_quizzes_ai WHERE user_id = ${learnerId}`) as Row[];
    const mock = (await s`SELECT COUNT(*)::int AS n FROM mock_exam_results WHERE user_id = ${learnerId}`) as Row[];
    return {
      weekly_quizzes_ai_generated: num(wk[0]?.gen),
      weekly_quizzes_ai_submitted: num(wk[0]?.submitted),
      mock_exam_results: num(mock[0]?.n),
    };
  });

  return Response.json({
    learner_id: learnerId,
    profile: { exists: Boolean(profile), subjects, has_persona: hasPersona },
    concept_mastery: mastery,
    skill_practice: skillPractice,
    chat_turns: chatTurns,
    learner_agent_notes: agentNotes,
    test_attempts: testAttempts,
    other_quiz_tables: otherQuizzes,
    hint: 'If concept_mastery.total_rows > 0 but shown_after_scope_filter is 0 (or much smaller), the SCOPE FILTER is hiding your progress. If total_rows is 0/stale, it is a WRITE-path bug.',
  });
}
