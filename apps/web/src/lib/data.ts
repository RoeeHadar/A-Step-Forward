import type { AuthContext } from './auth';
import type { LearnerDashboard } from '@asf/schemas/curriculum';
import type { LearnerProgress } from '@asf/schemas/progress';
import type { EducatorDashboard } from '@asf/schemas/progress';
import type { AdminStats } from '@asf/schemas/progress';
import type { Lesson } from '@asf/schemas/curriculum';
import type { MemoryRecord } from '@asf/schemas/memory';
import { learnerDashboardSchema } from '@asf/schemas/curriculum';
import { learnerProgressSchema, educatorDashboardSchema, adminStatsSchema } from '@asf/schemas/progress';
import { lessonSchema } from '@asf/schemas/curriculum';
import { memoryTimelineSchema } from '@asf/schemas/memory';
import { apiFetch, apiFetchOptional } from './api';

// Brand-new learners must NOT see fake "Introduction to Fractions" tiles.
// The real numbers come from `getDashboardSnapshot()` in `neon-db.ts`, which
// the `/app` server page calls directly. This fallback is now empty so any
// legacy caller of `fetchDashboard()` gets the same empty-state semantics:
// "no lessons yet" / "no mastery yet" rather than mock content.
const MOCK_DASHBOARD: LearnerDashboard = {
  recent_lessons: [],
  mastery_summary: [],
};

// Same reasoning as MOCK_DASHBOARD: a brand-new learner must never see
// fake fractions on /app/progress. If `/v1/progress` returns nothing the UI
// renders the empty state, not a fabricated history.
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

const MOCK_ADMIN: AdminStats = {
  total_learners: 1284,
  total_educators: 42,
  active_sessions_24h: 312,
  memory_writes_24h: 4521,
  avg_latency_ms: 890,
};

export async function fetchDashboard(auth: AuthContext): Promise<LearnerDashboard> {
  const remote = await apiFetchOptional('/v1/dashboard', {
    schema: learnerDashboardSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  return remote ?? { ...MOCK_DASHBOARD };
}

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

export async function fetchMemories(auth: AuthContext): Promise<MemoryRecord[]> {
  // Memory must be REAL — never fabricate entries. If the upstream timeline
  // returns nothing (brand-new learner, Render API unavailable, schema
  // mismatch), we hand back `[]` so `MemoryInspector` renders its already-
  // existing `t.noMemoriesYet` empty state ("No memories yet — start
  // chatting with an agent and we'll build a picture of how you learn.").
  // The previous fallback shipped two hardcoded sample entries
  // ("Prefers visual explanations…", "Completed lesson on fractions…")
  // which made the page look populated for users who had done nothing.
  const remote = await apiFetchOptional('/v1/memory/timeline?k=100', {
    schema: memoryTimelineSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  return remote ?? [];
}

export async function fetchEducatorDashboard(auth: AuthContext): Promise<EducatorDashboard> {
  const remote = await apiFetchOptional('/v1/educator/dashboard', {
    schema: educatorDashboardSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  return remote ?? MOCK_EDUCATOR;
}

export async function fetchAdminStats(auth: AuthContext): Promise<AdminStats> {
  const remote = await apiFetchOptional('/v1/admin/stats', {
    schema: adminStatsSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  return remote ?? MOCK_ADMIN;
}

export { apiFetch };
