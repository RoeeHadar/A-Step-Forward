/**
 * Neon-backed platform counts for /admin (no mock fallbacks).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import type { AdminStats } from '@asf/schemas/progress';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export type AdminPlatformStats = AdminStats & {
  pending_bookings: number;
  source: 'neon' | 'unavailable';
};

async function count(query: () => Promise<Record<string, unknown>[]>): Promise<number> {
  try {
    const rows = await query();
    const row = rows[0] ?? {};
    const raw = row.n ?? row.count ?? 0;
    return Number(raw) || 0;
  } catch {
    return 0;
  }
}

export async function fetchNeonAdminStats(): Promise<AdminPlatformStats> {
  if (!sql) {
    return {
      total_learners: 0,
      total_educators: 0,
      active_sessions_24h: 0,
      memory_writes_24h: 0,
      avg_latency_ms: 0,
      pending_bookings: 0,
      source: 'unavailable',
    };
  }

  const [total_learners, total_educators, active_sessions_24h, memory_writes_24h, pending_bookings] =
    await Promise.all([
      count(() => sql`SELECT COUNT(*)::int AS n FROM learner_profiles`),
      count(() => sql`SELECT COUNT(*)::int AS n FROM app_users WHERE role = 'educator'`),
      count(
        () => sql`
          SELECT COUNT(DISTINCT learner_id)::int AS n
          FROM chat_turns
          WHERE created_at > NOW() - INTERVAL '24 hours'
        `,
      ),
      count(
        () => sql`
          SELECT COUNT(*)::int AS n
          FROM learner_agent_notes
          WHERE created_at > NOW() - INTERVAL '24 hours'
        `,
      ),
      count(
        () => sql`
          SELECT COUNT(*)::int AS n
          FROM lesson_bookings
          WHERE status IN ('submitted', 'proposal_sent', 'pick_pending')
        `,
      ),
    ]);

  return {
    total_learners,
    total_educators,
    active_sessions_24h,
    memory_writes_24h,
    avg_latency_ms: 0,
    pending_bookings,
    source: 'neon',
  };
}
