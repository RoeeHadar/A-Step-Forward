/**
 * Learner XP ledger — durable gamification replacing estimated study minutes.
 * Awards are idempotent via UNIQUE(learner_id, source_id).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';
import {
  XP_PER_LEVEL,
  XP_REWARDS,
  MASTERY_XP_THRESHOLD,
  xpProgressInLevel,
  masterySourceId,
  streakSourceId,
} from '@/lib/learner-xp-math';

export {
  XP_REWARDS,
  XP_PER_LEVEL,
  MASTERY_XP_THRESHOLD,
  levelFromXp,
  xpProgressInLevel,
  masterySourceId,
  answerSourceId,
  streakSourceId,
  gateSourceId,
  quizPassSourceId,
} from '@/lib/learner-xp-math';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export type XpReason =
  | 'correct_answer'
  | 'mastery_threshold'
  | 'gate_pass'
  | 'quiz_pass'
  | 'streak_day'
  | 'backfill_mastery'
  | 'backfill_streak';

export interface XpEventRow {
  amount: number;
  reason: string;
  source_id: string;
  created_at: string;
}

export interface XpSnapshot {
  total_xp: number;
  level: number;
  into_level: number;
  to_next: number;
  week_xp: number;
  recent: XpEventRow[];
}

const EMPTY_SNAPSHOT: XpSnapshot = {
  total_xp: 0,
  level: 1,
  into_level: 0,
  to_next: XP_PER_LEVEL,
  week_xp: 0,
  recent: [],
};

let ensured = false;

export async function ensureXpTables(): Promise<boolean> {
  if (!sql) return false;
  if (ensured) return true;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS learner_xp_events (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        learner_id  TEXT NOT NULL,
        amount      INT NOT NULL,
        reason      TEXT NOT NULL,
        source_id   TEXT NOT NULL,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (learner_id, source_id)
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_learner_xp_events_learner_created
      ON learner_xp_events (learner_id, created_at DESC)`;
    await sql`
      ALTER TABLE learner_profiles
      ADD COLUMN IF NOT EXISTS total_xp INT NOT NULL DEFAULT 0
    `;
    ensured = true;
    return true;
  } catch (err) {
    logger.error('[learner-xp] ensureXpTables failed', { err: String(err) });
    return false;
  }
}

export interface AwardXpInput {
  learnerId: string;
  amount: number;
  reason: XpReason | string;
  sourceId: string;
}

export async function awardXp(input: AwardXpInput): Promise<number> {
  if (!sql) return 0;
  const amount = Math.floor(Number(input.amount) || 0);
  if (amount <= 0 || !input.learnerId || !input.sourceId) return 0;
  const ok = await ensureXpTables();
  if (!ok) return 0;
  try {
    const rows = await sql`
      INSERT INTO learner_xp_events (learner_id, amount, reason, source_id)
      VALUES (${input.learnerId}, ${amount}, ${input.reason}, ${input.sourceId})
      ON CONFLICT (learner_id, source_id) DO NOTHING
      RETURNING amount
    `;
    const inserted = Array.isArray(rows) && rows.length > 0;
    if (!inserted) return 0;
    await sql`
      UPDATE learner_profiles
      SET total_xp = COALESCE(total_xp, 0) + ${amount}
      WHERE learner_id = ${input.learnerId}
    `;
    return amount;
  } catch (err) {
    logger.warn('[learner-xp] awardXp failed', { err: String(err) });
    return 0;
  }
}

export async function getXpSnapshot(learnerId: string): Promise<XpSnapshot> {
  if (!sql || !learnerId) return { ...EMPTY_SNAPSHOT };
  const ok = await ensureXpTables();
  if (!ok) return { ...EMPTY_SNAPSHOT };
  try {
    const [totalRows, weekRows, recentRows] = await Promise.all([
      sql`
        SELECT COALESCE(
          (SELECT total_xp FROM learner_profiles WHERE learner_id = ${learnerId} LIMIT 1),
          (SELECT COALESCE(SUM(amount), 0)::int FROM learner_xp_events WHERE learner_id = ${learnerId}),
          0
        )::int AS total
      `,
      sql`
        SELECT COALESCE(SUM(amount), 0)::int AS n
        FROM learner_xp_events
        WHERE learner_id = ${learnerId}
          AND created_at >= NOW() - INTERVAL '7 days'
      `,
      sql`
        SELECT amount, reason, source_id, created_at::text AS created_at
        FROM learner_xp_events
        WHERE learner_id = ${learnerId}
        ORDER BY created_at DESC
        LIMIT 3
      `,
    ]);
    const total = Number((totalRows as Array<{ total: number }>)[0]?.total ?? 0);
    const week_xp = Number((weekRows as Array<{ n: number }>)[0]?.n ?? 0);
    const progress = xpProgressInLevel(total);
    return {
      total_xp: total,
      level: progress.level,
      into_level: progress.into_level,
      to_next: progress.to_next,
      week_xp,
      recent: (recentRows as XpEventRow[]).map((r) => ({
        amount: Number(r.amount),
        reason: String(r.reason),
        source_id: String(r.source_id),
        created_at: String(r.created_at),
      })),
    };
  } catch (err) {
    logger.warn('[learner-xp] getXpSnapshot failed', { err: String(err) });
    return { ...EMPTY_SNAPSHOT };
  }
}

async function syncTotalXpFromLedger(learnerId: string): Promise<void> {
  if (!sql) return;
  try {
    await sql`
      UPDATE learner_profiles
      SET total_xp = (
        SELECT COALESCE(SUM(amount), 0)::int
        FROM learner_xp_events
        WHERE learner_id = ${learnerId}
      )
      WHERE learner_id = ${learnerId}
    `;
  } catch {
    // ignore
  }
}

export async function backfillLearnerXp(learnerId: string): Promise<number> {
  if (!sql || !learnerId) return 0;
  const ok = await ensureXpTables();
  if (!ok) return 0;
  let awarded = 0;
  try {
    const masteryRows = (await sql`
      SELECT concept_id
      FROM concept_mastery
      WHERE learner_id = ${learnerId} AND score >= ${MASTERY_XP_THRESHOLD}
    `) as Array<{ concept_id: string }>;
    for (const row of masteryRows) {
      awarded += await awardXp({
        learnerId,
        amount: XP_REWARDS.mastery_threshold,
        reason: 'backfill_mastery',
        sourceId: masterySourceId(row.concept_id),
      });
    }

    const dayRows = (await sql`
      SELECT d::text AS day FROM (
        SELECT DISTINCT DATE(last_activity) AS d
        FROM concept_mastery
        WHERE learner_id = ${learnerId} AND last_activity IS NOT NULL
          AND last_activity >= NOW() - INTERVAL '30 days'
        UNION
        SELECT DISTINCT DATE(last_practiced) AS d
        FROM skill_practice
        WHERE learner_id = ${learnerId} AND last_practiced IS NOT NULL
          AND last_practiced >= NOW() - INTERVAL '30 days'
        UNION
        SELECT DISTINCT DATE(created_at) AS d
        FROM chat_turns
        WHERE learner_id = ${learnerId} AND role = 'user'
          AND created_at >= NOW() - INTERVAL '30 days'
      ) days
      WHERE d IS NOT NULL
      ORDER BY d DESC
      LIMIT 14
    `) as Array<{ day: string }>;
    for (const row of dayRows) {
      const day = String(row.day).slice(0, 10);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) continue;
      awarded += await awardXp({
        learnerId,
        amount: XP_REWARDS.streak_day,
        reason: 'backfill_streak',
        sourceId: streakSourceId(day),
      });
    }

    if (awarded > 0) await syncTotalXpFromLedger(learnerId);
  } catch (err) {
    logger.warn('[learner-xp] backfillLearnerXp failed', { err: String(err) });
  }
  return awarded;
}

export async function ensureXpSnapshot(learnerId: string): Promise<XpSnapshot> {
  if (!learnerId) return { ...EMPTY_SNAPSHOT };
  await ensureXpTables();
  try {
    if (sql) {
      const countRows = (await sql`
        SELECT COUNT(*)::int AS n FROM learner_xp_events WHERE learner_id = ${learnerId}
      `) as Array<{ n: number }>;
      if (Number(countRows[0]?.n ?? 0) === 0) {
        const masteryN = (await sql`
          SELECT COUNT(*)::int AS n FROM concept_mastery
          WHERE learner_id = ${learnerId} AND score >= ${MASTERY_XP_THRESHOLD}
        `) as Array<{ n: number }>;
        if (Number(masteryN[0]?.n ?? 0) > 0) {
          await backfillLearnerXp(learnerId);
        }
      }
    }
  } catch {
    // continue
  }
  return getXpSnapshot(learnerId);
}

export async function maybeAwardMasteryXp(
  learnerId: string,
  conceptId: string,
): Promise<number> {
  if (!sql || !learnerId || !conceptId) return 0;
  try {
    const rows = (await sql`
      SELECT score::float AS score
      FROM concept_mastery
      WHERE learner_id = ${learnerId} AND concept_id = ${conceptId}
      LIMIT 1
    `) as Array<{ score: number }>;
    if (Number(rows[0]?.score ?? 0) < MASTERY_XP_THRESHOLD) return 0;
    return awardXp({
      learnerId,
      amount: XP_REWARDS.mastery_threshold,
      reason: 'mastery_threshold',
      sourceId: masterySourceId(conceptId),
    });
  } catch {
    return 0;
  }
}

export async function maybeAwardStreakXp(learnerId: string, dayIso?: string): Promise<number> {
  const day = dayIso?.slice(0, 10) || new Date().toISOString().slice(0, 10);
  return awardXp({
    learnerId,
    amount: XP_REWARDS.streak_day,
    reason: 'streak_day',
    sourceId: streakSourceId(day),
  });
}

export function formatXpContextBlock(snap: XpSnapshot, locale: 'he' | 'en' = 'he'): string {
  const reasonLabel = (r: string) => {
    const map: Record<string, { he: string; en: string }> = {
      correct_answer: { he: 'תשובה נכונה', en: 'correct answer' },
      mastery_threshold: { he: 'שליטה בנושא', en: 'concept mastery' },
      gate_pass: { he: 'מעבר שער שבועי', en: 'week gate pass' },
      quiz_pass: { he: 'מעבר מבחן', en: 'quiz pass' },
      streak_day: { he: 'יום רצף', en: 'streak day' },
      backfill_mastery: { he: 'שליטה (היסטוריה)', en: 'mastery (backfill)' },
      backfill_streak: { he: 'רצף (היסטוריה)', en: 'streak (backfill)' },
    };
    const m = map[r];
    return m ? (locale === 'he' ? m.he : m.en) : r;
  };
  const recent =
    snap.recent.length === 0
      ? locale === 'he'
        ? 'אין אירועים אחרונים'
        : 'no recent events'
      : snap.recent
          .map((e) => `+${e.amount} ${reasonLabel(e.reason)}`)
          .join(locale === 'he' ? ' · ' : '; ');
  if (locale === 'he') {
    return [
      '## XP של הלומד (פנימי — אל תדביק גולמי)',
      `- סה״כ XP: ${snap.total_xp} · רמה ${snap.level} (עוד ${snap.to_next} לרמה הבאה)`,
      `- XP בשבוע האחרון: ${snap.week_xp}`,
      `- אחרונים: ${recent}`,
      '- אל תמציא XP; השתמש רק במספרים האלה. XP משקף פעולות למידה, לא זמן שעון.',
      '- כשמספרים סטטוס ללומד: נסח בעברית פשוטה (רמה + התקדמות), בלי שורות XP גולמיות ובלי רשימות אירועים כפולות.',
    ].join('\n');
  }
  return [
    '## Learner XP (internal — do not paste raw)',
    `- Total XP: ${snap.total_xp} · Level ${snap.level} (${snap.to_next} XP to next)`,
    `- XP last 7 days: ${snap.week_xp}`,
    `- Recent: ${recent}`,
    '- Do not invent XP; use only these numbers. XP reflects learning actions, not clock time.',
    '- When reporting status: plain paraphrase (level + progress); never dump raw XP lines or duplicate event lists.',
  ].join('\n');
}
