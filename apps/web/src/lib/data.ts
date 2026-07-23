import type { AuthContext } from './auth';
import type { LearnerProgress } from '@asf/schemas/progress';
import type { EducatorDashboard } from '@asf/schemas/progress';
import type { Lesson } from '@asf/schemas/curriculum';
import { learnerProgressSchema, educatorDashboardSchema } from '@asf/schemas/progress';
import { lessonSchema } from '@asf/schemas/curriculum';
import { apiFetch, apiFetchOptional } from './api';
import type { AdminPlatformStats } from './admin-stats-db';

// Dashboard + memory timelines: use GET /api/dashboard and GET /api/memory (Neon-direct).
// Server pages use helpers in neon-db.ts (getDashboardSnapshot, getLearnerMemorySnapshot).

// Brand-new learners must NOT see fake progress on /app/progress. If `/v1/progress`
// returns nothing the UI renders the empty state, not a fabricated history.
const MOCK_PROGRESS: LearnerProgress = {
  learner_id: 'demo',
  streak_days: 0,
  total_minutes: 0,
  lessons_completed: 0,
  concepts: [],
};

const MOCK_EDUCATOR: EducatorDashboard = {
  class_avg_mastery: 0.58,
  active_today: 14,
  learners: [
    {
      learner_id: 'l1',
      display_name: 'Alex Chen',
      avg_mastery: 0.78,
      at_risk: false,
      last_active_at: new Date().toISOString(),
    },
    {
      learner_id: 'l2',
      display_name: 'Sam Rivera',
      avg_mastery: 0.42,
      at_risk: true,
      last_active_at: new Date(Date.now() - 172800000).toISOString(),
    },
  ],
};

export async function fetchLesson(auth: AuthContext, lessonId: string): Promise<Lesson | null> {
  const remote = await apiFetchOptional(`/v1/lessons/${lessonId}`, {
    schema: lessonSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  if (remote) return remote;

  const { getSeedLesson } = await import('./seed-lessons');
  return getSeedLesson(lessonId);
}

/**
 * Public-facing lesson fetch.
 *
 * The `/v1/lessons/{id}` route still requires an auth header in dev/test envs,
 * so we send a `demo` learner id to satisfy the dev fallback. When the API is
 * unreachable (returns null), we fall through to the committed seed snapshot
 * so the demo URL always renders something for the foundations-of-math course.
 */
export async function fetchLessonPublic(lessonId: string): Promise<Lesson | null> {
  const remote = await apiFetchOptional(`/v1/lessons/${lessonId}`, {
    schema: lessonSchema,
    auth: { learnerId: 'demo-public', role: 'learner' },
  });
  if (remote) return remote;

  const { getSeedLesson } = await import('./seed-lessons');
  return getSeedLesson(lessonId);
}

export async function fetchProgress(auth: AuthContext): Promise<LearnerProgress> {
  const remote = await apiFetchOptional('/v1/progress', {
    schema: learnerProgressSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  return remote ?? { ...MOCK_PROGRESS, learner_id: auth.learnerId };
}

export async function fetchEducatorDashboard(auth: AuthContext): Promise<EducatorDashboard> {
  const remote = await apiFetchOptional('/v1/educator/dashboard', {
    schema: educatorDashboardSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  return remote ?? MOCK_EDUCATOR;
}

/** Live Neon counts only — never returns fabricated demo numbers. */
export async function fetchAdminStats(auth: AuthContext): Promise<AdminPlatformStats> {
  void auth;
  const { fetchNeonAdminStats } = await import('./admin-stats-db');
  return fetchNeonAdminStats();
}

export { apiFetch };
