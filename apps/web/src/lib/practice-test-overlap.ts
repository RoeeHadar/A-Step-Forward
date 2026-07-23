/**
 * Soft anti-overlap between practice arena and archived tests/gates.
 * Exact source_question_id matches from recent attempts are skipped in practice;
 * thematic overlap (same skill, different numbers) remains allowed.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { ensureTestAttemptsTable } from '@/lib/test-attempts';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export async function listRecentTestSourceQuestionIds(
  learnerId: string,
  limitAttempts = 12,
): Promise<Set<string>> {
  const out = new Set<string>();
  if (!sql) return out;
  try {
    await ensureTestAttemptsTable();
    const rows = (await sql`
      SELECT questions
      FROM test_attempts
      WHERE learner_id = ${learnerId}
      ORDER BY created_at DESC
      LIMIT ${limitAttempts}
    `) as Array<{ questions: unknown }>;

    for (const row of rows) {
      const qs = row.questions;
      if (!Array.isArray(qs)) continue;
      for (const q of qs) {
        if (!q || typeof q !== 'object') continue;
        const o = q as Record<string, unknown>;
        const sid =
          (typeof o.source_question_id === 'string' && o.source_question_id) ||
          (typeof o.question_id === 'string' && o.question_id) ||
          null;
        if (sid) out.add(sid);
      }
    }
  } catch (err) {
    console.warn('[practice-test-overlap] list failed', err);
  }
  return out;
}
