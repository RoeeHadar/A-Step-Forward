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

const MOCK_DASHBOARD: LearnerDashboard = {
  recent_lessons: [
    {
      id: 'lesson-intro-fractions',
      title: 'Introduction to Fractions',
      progress: 0.65,
      est_minutes: 20,
      last_accessed_at: new Date().toISOString(),
    },
    {
      id: 'lesson-fractions-ops',
      title: 'Adding and Subtracting Fractions',
      progress: 0.2,
      est_minutes: 25,
      last_accessed_at: new Date(Date.now() - 86400000).toISOString(),
    },
  ],
  mastery_summary: [
    { concept_id: 'concept-fractions', concept_name: 'Fractions', score: 0.72 },
    { concept_id: 'concept-decimals', concept_name: 'Decimals', score: 0.45 },
    { concept_id: 'concept-ratios', concept_name: 'Ratios', score: 0.3 },
  ],
};

const MOCK_LESSON: Lesson = {
  id: 'lesson-intro-fractions',
  title: 'Introduction to Fractions',
  body_md: `# Introduction to Fractions

A **fraction** represents a part of a whole.

## Key concepts

- **Numerator** — how many parts you have
- **Denominator** — how many equal parts the whole is divided into

## Example

If you eat 3 slices of a pizza cut into 8 equal slices, you've eaten $\\frac{3}{8}$ of the pizza.

> Try explaining this to the Tutor agent — they'll guide you with questions rather than giving away the answer.`,
  modality: 'interactive',
  objectives: [
    {
      id: 'obj-1',
      statement: 'Identify numerator and denominator in a given fraction',
      blooms_level: 'understand',
      concepts: ['concept-fractions'],
    },
  ],
  concepts: ['concept-fractions'],
  resources: [],
  est_minutes: 20,
};

const MOCK_PROGRESS: LearnerProgress = {
  learner_id: 'demo',
  streak_days: 5,
  total_minutes: 340,
  lessons_completed: 12,
  concepts: [
    {
      concept_id: 'concept-fractions',
      concept_name: 'Fractions',
      current_score: 0.72,
      history: [
        { date: '2026-06-01', score: 0.4 },
        { date: '2026-06-08', score: 0.55 },
        { date: '2026-06-15', score: 0.65 },
        { date: '2026-06-22', score: 0.72 },
      ],
    },
    {
      concept_id: 'concept-decimals',
      concept_name: 'Decimals',
      current_score: 0.45,
      history: [
        { date: '2026-06-01', score: 0.2 },
        { date: '2026-06-15', score: 0.35 },
        { date: '2026-06-22', score: 0.45 },
      ],
    },
  ],
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

export async function fetchLesson(auth: AuthContext, lessonId: string): Promise<Lesson> {
  const remote = await apiFetchOptional(`/v1/lessons/${lessonId}`, {
    schema: lessonSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  if (remote) return remote;

  // Fall back to the committed seed snapshot so the demo content is always
  // accurate (the previous mock hard-coded "Introduction to Fractions"
  // regardless of which lesson the learner requested).
  const { getSeedLesson } = await import('./seed-lessons');
  const seeded = getSeedLesson(lessonId);
  if (seeded) return seeded;
  return { ...MOCK_LESSON, id: lessonId };
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
  const remote = await apiFetchOptional('/v1/memory/timeline?k=100', {
    schema: memoryTimelineSchema,
    auth: { learnerId: auth.learnerId, role: auth.role },
  });
  if (remote && remote.length > 0) return remote;

  return [
    {
      id: 'mem-1',
      learner_id: auth.learnerId,
      type: 'semantic',
      content: 'Prefers visual explanations with diagrams',
      summary: 'Learning preference',
      tags: ['preference', 'visual'],
      salience: 0.8,
      confidence: 0.9,
      valence: 0.5,
      decay_tau_days: 30,
      access_count: 12,
      provenance: { kind: 'chat', agent: 'tutor', id: 'session-1' },
      kg_node_ids: [],
    },
    {
      id: 'mem-2',
      learner_id: auth.learnerId,
      type: 'episodic',
      content: 'Completed lesson on fractions — struggled with unlike denominators',
      summary: 'Fraction lesson session',
      tags: ['fractions', 'lesson'],
      salience: 0.6,
      confidence: 0.85,
      valence: -0.2,
      decay_tau_days: 14,
      access_count: 3,
      provenance: { kind: 'lesson', id: 'lesson-intro-fractions' },
      kg_node_ids: ['concept-fractions'],
    },
  ];
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
