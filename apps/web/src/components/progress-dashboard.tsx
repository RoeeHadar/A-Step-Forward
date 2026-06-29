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
  userId,
  hasPhysicsEnrollment = false,
}: {
  progress: LearnerProgress;
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

  const showDualGrades =
    hasPhysicsEnrollment &&
    gradeEstimate != null &&
    physicsGradeEstimate != null &&
    gradeEstimate.subject !== 'hs_physics';

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

  const historyData =
    progress.concepts[0]?.history.map((h) => ({
      date: h.date.slice(5),
      score: Math.round(h.score * 100),
    })) ?? [];

  const topConceptName =
    progress.concepts[0] != null
      ? isHe &&
        (progress.concepts[0] as typeof progress.concepts[0] & {
          concept_name_he?: string | null;
        }).concept_name_he
        ? (progress.concepts[0] as typeof progress.concepts[0] & {
            concept_name_he?: string | null;
          }).concept_name_he!
        : progress.concepts[0].concept_name
      : '';

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
              <AnimatedCounter end={progress.streak_days} className="font-display text-3xl font-bold" />
              <span className="ms-1 text-lg font-normal text-muted-foreground">{t.days}</span>
            </>
          }
          gradient="from-accent-amber to-accent-magenta"
        />
        <StatCard
          title={t.totalTime}
          value={
            <>
              <AnimatedCounter end={progress.total_minutes} className="font-display text-3xl font-bold" />
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
              end={progress.lessons_completed}
              className="font-display text-3xl font-bold"
            />
          }
          gradient="from-accent-magenta to-accent-cyan"
        />
      </div>

      <div className="card-punch rounded-2xl p-6">
        <h2 className="font-display text-xl font-semibold">{t.masteryByConcept}</h2>
        <p className="mt-1 text-sm text-muted-foreground">{t.masteryByConceptDesc}</p>

        {showDualGrades ? (
          <div className="mt-3 space-y-1">
            <p className="text-sm font-semibold text-foreground">
              {isHe ? 'מוכנות לבגרות' : 'Bagrut Readiness'}
            </p>
            {gradeEstimate ? (
              <GradeEstimateRow
                estimate={gradeEstimate}
                isHe={isHe}
                practiceMoreLabel={t.practiceMoreForEstimate}
                withTrackLabel={withTrackLabel}
              />
            ) : null}
            {physicsGradeEstimate ? (
              <GradeEstimateRow
                estimate={physicsGradeEstimate}
                isHe={isHe}
                practiceMoreLabel={t.practiceMoreForEstimate}
                withTrackLabel={withTrackLabel}
              />
            ) : null}
          </div>
        ) : (
          <>
            {gradeEstimate != null && gradeEstimate.subject !== 'hs_physics' ? (
              <div className="mt-2">
                <GradeEstimateRow
                  estimate={gradeEstimate}
                  isHe={isHe}
                  practiceMoreLabel={t.practiceMoreForEstimate}
                  withTrackLabel={withTrackLabel}
                />
              </div>
            ) : null}
            {hasPhysicsEnrollment && physicsGradeEstimate != null ? (
              <div className="mt-2">
                {physicsGradeEstimate.masteryAvg < 0.3 ? (
                  <p className="text-sm italic text-muted-foreground">{t.practiceMoreForEstimate}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {isHe
                      ? `ציון משוער (פיזיקה): ~${physicsGradeEstimate.estimatedGrade}`
                      : `Estimated grade (Physics): ~${physicsGradeEstimate.estimatedGrade}`}
                  </p>
                )}
              </div>
            ) : null}
          </>
        )}

        <div className="mt-4 h-72">
          {masteryData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
              {t.noMasteryYet}
            </div>
          ) : (
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
                  name="Mastery %"
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {historyData.length > 0 ? (
        <div className="card-punch rounded-2xl p-6">
          <h2 className="font-display text-xl font-semibold">{t.masteryOverTime}</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {topConceptName} {t.progressTrend}
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="hsl(var(--accent-cyan))"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  name="Mastery %"
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
    <div className="card-punch rounded-2xl p-5">
      <p className="text-sm text-muted-foreground">{title}</p>
      <div className={`mt-1 bg-gradient-to-r bg-clip-text text-transparent ${gradient}`}>{value}</div>
    </div>
  );
}
