'use client';

import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { Share2 } from 'lucide-react';
import type { LearnerProgress } from '@asf/schemas/progress';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';
import { AnimatedCounter } from '@/components/animated-counter';
import { ActivityHeatmap } from '@/components/activity-heatmap';
import { LearnerStreakCard } from '@/components/learner-streak-card';
import type { ProgressSnapshot } from '@/lib/neon-db';

type GradeEstimate = {
  estimatedGrade: number;
  masteryAvg: number;
  subject?: string;
};

function trackLabelForSubject(subject: string | undefined, isHe: boolean): string {
  const s = subject ?? 'math_5';
  if (s === 'hs_physics') return isHe ? 'פיזיקה' : 'Physics';
  const units = s.match(/math_(\d)/)?.[1];
  if (units) return isHe ? `${units} יחידות` : `${units}pt math`;
  return isHe ? '5 יחידות' : '5pt math';
}

function GradeEstimateRow({
  estimate,
  isHe,
  practiceMoreLabel,
  withTrackLabel,
}: {
  estimate: GradeEstimate;
  isHe: boolean;
  practiceMoreLabel: string;
  withTrackLabel: (track: string, grade: string) => string;
}) {
  const track = trackLabelForSubject(estimate.subject, isHe);
  if (estimate.masteryAvg < 0.3) {
    return <p className="text-sm italic text-muted-foreground">{practiceMoreLabel}</p>;
  }
  return (
    <p className="text-sm text-muted-foreground">
      {withTrackLabel(track, String(estimate.estimatedGrade))}
    </p>
  );
}

export function ProgressDashboard({
  progress,
  snapshot,
  userId,
  hasPhysicsEnrollment = false,
}: {
  progress: LearnerProgress;
  snapshot: ProgressSnapshot;
  userId?: string;
  hasPhysicsEnrollment?: boolean;
}) {
  const { messages, locale } = useI18n();
  const t = messages.progress;
  const isHe = locale === 'he';

  const [gradeEstimate, setGradeEstimate] = useState<GradeEstimate | null>(null);
  const [physicsGradeEstimate, setPhysicsGradeEstimate] = useState<GradeEstimate | null>(null);
  const [shareToastVisible, setShareToastVisible] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void fetch('/api/progress/estimated-grade')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data && typeof data.estimatedGrade === 'number') {
          setGradeEstimate({
            estimatedGrade: data.estimatedGrade,
            masteryAvg: Number(data.masteryAvg ?? 0),
            subject: typeof data.subject === 'string' ? data.subject : undefined,
          });
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!hasPhysicsEnrollment) return;
    let cancelled = false;
    void fetch('/api/progress/estimated-grade?subject=hs_physics')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data && typeof data.estimatedGrade === 'number') {
          setPhysicsGradeEstimate({
            estimatedGrade: data.estimatedGrade,
            masteryAvg: Number(data.masteryAvg ?? 0),
            subject: 'hs_physics',
          });
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [hasPhysicsEnrollment]);

  const readinessRows = [
    gradeEstimate && gradeEstimate.subject !== 'hs_physics' ? gradeEstimate : null,
    hasPhysicsEnrollment ? physicsGradeEstimate : null,
  ].filter(Boolean) as GradeEstimate[];

  const showReadinessBlock = readinessRows.length > 0;

  async function handleShareProgress() {
    if (!userId) return;
    const url = `${window.location.origin}/progress/share/${userId}`;
    try {
      await navigator.clipboard.writeText(url);
      setShareToastVisible(true);
      window.setTimeout(() => setShareToastVisible(false), 4000);
    } catch {
      // Clipboard may be unavailable in some contexts.
    }
  }

  const masteryData = progress.concepts.map((c) => {
    const row = c as typeof c & { concept_name_he?: string | null };
    const name =
      isHe && row.concept_name_he ? row.concept_name_he : c.concept_name;
    return {
      name,
      score: Math.round(c.current_score * 100),
    };
  });

  const activityTrend = snapshot.daily_activity.map((d) => ({
    date: d.date.slice(5),
    actions: d.count,
  }));
  const hasActivityTrend = activityTrend.some((d) => d.actions > 0);

  const avgMasteryPct = Math.round(snapshot.avg_mastery * 100);

  const withTrackLabel = (track: string, grade: string) =>
    t.estimatedGradeWithTrack.replace('{track}', track).replace('{grade}', grade);

  return (
    <div className="space-y-6">
      {userId ? (
        <div className="flex flex-wrap items-center gap-3">
          <Button type="button" variant="outline" className="gap-2" onClick={() => void handleShareProgress()}>
            <Share2 className="h-4 w-4" aria-hidden />
            {isHe ? 'שתף התקדמות' : 'Share progress'}
          </Button>
        </div>
      ) : null}

      {shareToastVisible ? (
        <div
          role="status"
          aria-live="polite"
          className={cn(
            'fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-xl border border-border bg-card px-5 py-3 text-sm font-medium shadow-lg',
            'animate-in fade-in slide-in-from-bottom-4 duration-300',
          )}
          dir={isHe ? 'rtl' : 'ltr'}
        >
          {isHe
            ? 'הקישור הועתק! שתף עם הורה או מורה'
            : 'Link copied! Share with a parent or teacher'}
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          title={t.streak}
          value={
            <>
              <AnimatedCounter
                key={`streak-${progress.streak_days}`}
                end={progress.streak_days}
                className="font-display text-3xl font-bold"
              />
              <span className="ms-1 text-lg font-normal text-muted-foreground">{t.days}</span>
            </>
          }
          gradient="from-accent-amber to-accent-magenta"
        />
        <StatCard
          title={t.totalTime}
          value={
            <>
              <AnimatedCounter
                key={`minutes-${progress.total_minutes}`}
                end={progress.total_minutes}
                className="font-display text-3xl font-bold"
              />
              <span className="ms-1 text-lg font-normal text-muted-foreground">
                {messages.dashboard.minutes}
              </span>
            </>
          }
          gradient="from-accent-cyan to-primary"
        />
        <StatCard
          title={t.lessonsDone}
          value={
            <AnimatedCounter
              key={`lessons-${progress.lessons_completed}`}
              end={progress.lessons_completed}
              className="font-display text-3xl font-bold"
            />
          }
          gradient="from-accent-magenta to-accent-cyan"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ActivityHeatmap daily={snapshot.daily_activity} weekly={snapshot.weekly_recap} />
        <LearnerStreakCard streak={snapshot.streak} activity={snapshot.recent_activity} />
      </div>

      <div className="card-punch rounded-2xl p-6">
        <h2 className="font-display text-xl font-semibold">{t.masteryByConcept}</h2>
        <p className="mt-1 text-sm text-muted-foreground">{t.masteryByConceptDesc}</p>

        {showReadinessBlock ? (
          <div className="mt-3 space-y-1">
            <p className="text-sm font-semibold text-foreground">
              {isHe ? 'מוכנות לבגרות' : 'Bagrut Readiness'}
            </p>
            {readinessRows.map((estimate) => {
              const isPhysics = estimate.subject === 'hs_physics';
              if (isPhysics) {
                return estimate.masteryAvg < 0.3 ? (
                  <p key="physics" className="text-sm italic text-muted-foreground">
                    {t.practiceMoreForEstimate}
                  </p>
                ) : (
                  <p key="physics" className="text-sm text-muted-foreground">
                    {isHe
                      ? `ציון משוער (פיזיקה): ~${estimate.estimatedGrade}`
                      : `Estimated grade (Physics): ~${estimate.estimatedGrade}`}
                  </p>
                );
              }
              return (
                <GradeEstimateRow
                  key={estimate.subject ?? 'math'}
                  estimate={estimate}
                  isHe={isHe}
                  practiceMoreLabel={t.practiceMoreForEstimate}
                  withTrackLabel={withTrackLabel}
                />
              );
            })}
          </div>
        ) : null}

        <div className="mt-4 h-72">
          {masteryData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
              {t.noMasteryYet}
            </div>
          ) : (
            <>
              {avgMasteryPct > 0 ? (
                <p className="mb-3 text-sm text-muted-foreground">
                  {isHe
                    ? `ממוצע שליטה: ${avgMasteryPct}% · ${snapshot.atoms_practiced} מיומנויות שתורגלו`
                    : `Average mastery: ${avgMasteryPct}% · ${snapshot.atoms_practiced} atoms practiced`}
                </p>
              ) : null}
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={masteryData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar
                    dataKey="score"
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                    name={isHe ? 'שליטה %' : 'Mastery %'}
                  />
                </BarChart>
              </ResponsiveContainer>
            </>
          )}
        </div>
      </div>

      {hasActivityTrend ? (
        <div className="card-punch rounded-2xl p-6">
          <h2 className="font-display text-xl font-semibold">
            {isHe ? 'פעילות לאורך זמן' : 'Activity over time'}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {isHe
              ? 'מספר הפעולות (צ׳אט, שיעורים, תרגול) ב-30 הימים האחרונים'
              : 'Learning actions (chat, lessons, practice) over the last 30 days'}
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={activityTrend} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="actions"
                  stroke="hsl(var(--accent-cyan))"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  name={isHe ? 'פעולות' : 'Actions'}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function StatCard({
  title,
  value,
  gradient,
}: {
  title: string;
  value: ReactNode;
  gradient: string;
}) {
  return (
    <div className="card-punch relative overflow-hidden rounded-2xl p-5">
      <span
        className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r opacity-80 ${gradient}`}
        aria-hidden
      />
      <p className="text-sm text-muted-foreground">{title}</p>
      <div className="mt-1 text-foreground">{value}</div>
    </div>
  );
}
