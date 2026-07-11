'use client';

import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '@/components/page-header';
import { ProgressDashboard } from '@/components/progress-dashboard';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';
import type { ProgressSnapshot } from '@/lib/neon-db';

function snapshotToProgress(snapshot: ProgressSnapshot, learnerId: string) {
  return {
    learner_id: learnerId,
    streak_days: snapshot.streak.current_days,
    total_minutes: snapshot.total_minutes,
    lessons_completed: snapshot.lessons_completed,
    concepts: snapshot.concepts.map((c) => ({
      concept_id: c.concept_id,
      concept_name: c.concept_name,
      concept_name_he: c.concept_name_he,
      current_score: c.current_score,
      history: c.history,
    })),
  };
}

export function ProgressPageContent({
  snapshot,
  learnerId,
  hasPhysicsEnrollment = false,
}: {
  snapshot: ProgressSnapshot | null;
  learnerId: string;
  hasPhysicsEnrollment?: boolean;
}) {
  const { messages, locale } = useI18n();
  const router = useRouter();
  const refreshLabel = locale === 'he' ? 'רענון' : 'Refresh';

  const resolved =
    snapshot ??
    ({
      streak: {
        current_days: 0,
        longest_days: 0,
        last_active: null,
        active_today: false,
        active_days_last_30: 0,
      },
      total_minutes: 0,
      lessons_completed: 0,
      avg_mastery: 0,
      atoms_practiced: 0,
      concepts: [],
      daily_activity: [],
      weekly_recap: {
        week_start: '',
        week_end: '',
        chat_turns: 0,
        concepts_touched: 0,
        atoms_practiced: 0,
        mastery_gain: 0,
        best_day: null,
      },
      recent_activity: [],
    } satisfies ProgressSnapshot);

  return (
    <div>
      <PageHeader
        title={messages.progress.title}
        description={messages.progress.description}
        gradientTitle
        actions={
          <Button type="button" variant="outline" size="sm" onClick={() => router.refresh()}>
            <RefreshCw className="me-2 h-4 w-4" aria-hidden />
            {refreshLabel}
          </Button>
        }
      />
      <ProgressDashboard
        progress={snapshotToProgress(resolved, learnerId)}
        snapshot={resolved}
        userId={learnerId}
        hasPhysicsEnrollment={hasPhysicsEnrollment}
      />
    </div>
  );
}
