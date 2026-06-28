'use client';

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
import type { LearnerProgress } from '@asf/schemas/progress';
import { useI18n } from '@/providers/i18n-provider';
import { AnimatedCounter } from '@/components/animated-counter';

export function ProgressDashboard({ progress }: { progress: LearnerProgress }) {
  const { messages, locale } = useI18n();
  const t = messages.progress;
  const isHe = locale === 'he';

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

  return (
    <div className="space-y-6">
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
