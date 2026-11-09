import type { AuthContext } from './auth';
import { apiFetch } from './api';
import type { AdminPlatformStats } from './admin-stats-db';

// Dashboard + memory timelines: use GET /api/dashboard and GET /api/memory (Neon-direct).
// Server pages use helpers in neon-db.ts (getDashboardSnapshot, getLearnerMemorySnapshot).
// AS-105: the four unreferenced Render fetches (lesson, public lesson, progress and the
// unhandled educator dashboard) were removed; lessons render from the seed snapshot
// (lib/seed-lessons) and progress from Neon (neon-db.ts).

/** Live Neon counts only — never returns fabricated demo numbers. */
export async function fetchAdminStats(auth: AuthContext): Promise<AdminPlatformStats> {
  void auth;
  const { fetchNeonAdminStats } = await import('./admin-stats-db');
  return fetchNeonAdminStats();
}

export { apiFetch };
