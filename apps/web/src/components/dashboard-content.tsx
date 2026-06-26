'use client';

import type { ComponentType, ReactNode } from 'react';
import Link from 'next/link';
import { Flame, CheckCircle2, Star } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Progress } from '@asf/ui/progress';
import { cn } from '@asf/ui';
import { agentDisplayNames, type AgentName } from '@asf/schemas/agents';
import { useI18n } from '@/providers/i18n-provider';
import { AnimatedCounter } from '@/components/animated-counter';
import type { DashboardSnapshot } from '@/lib/neon-db';

/**
 * /app dashboard content. Every number on this page is REAL (sourced from
 * Neon via `getDashboardSnapshot`); there is no mock fallback. A brand-new
 * learner sees zeros + "no lessons yet" / "no mastery yet" empty states.
 *
 * `streak_days` comes from chat turns + concept mastery activity + skill
 * practice unioned via `getLearnerStreak`. `lessons_completed` is the
 * count of distinct concepts with `concept_mastery.score >= 0.7`. `level`
 * is a deterministic gamification curve based on completions + atoms
 * practiced — it stays at 1 until the learner actually does work.
 */

const progressBarClass =
  'h-2.5 overflow-hidden rounded-full bg-secondary [&>div]:rounded-full [&>div]:bg-gradient-to-r [&>div]:from-primary [&>div]:to-accent-cyan';

const dashboardAgents: Array<{
  agent: AgentName;
  emoji: string;
  gradientClass: string;
}> = [
  { agent: 'tutor', emoji: '📚', gradientClass: 'from-primary to-accent-magenta' },
  { agent: 'mentor', emoji: '🌟', gradientClass: 'from-accent-amber to-accent-magenta' },
  { agent: 'coach', emoji: '💪', gradientClass: 'from-accent-cyan to-primary' },
  { agent: 'reviewer', emoji: '✍️', gradientClass: 'from-accent-magenta to-accent-cyan' },
];

export function DashboardContent({
  displayName,
  snapshot,
}: {
  displayName: string;
  snapshot: DashboardSnapshot;
}) {
  const { messages, locale } = useI18n();
  const t = messages.dashboard;
  const isHe = locale === 'he';
  const { stats, recent_lessons, mastery_summary } = snapshot;

  return (
    <div dir={isHe ? 'rtl' : 'ltr'}>
      <header className="mb-8">
        <h1 className="font-display text-4xl font-bold tracking-tight">
          <span className="bg-gradient-to-r from-primary via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
            {t.welcomeBack}, {displayName}
          </span>
        </h1>
        <p className="mt-2 text-muted-foreground">{t.continueJourney}</p>
      </header>

      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <StatTile
          icon={Flame}
          label={t.streak}
          value={
            <AnimatedCounter
              end={stats.streak_days}
              className="font-display text-3xl font-bold"
            />
          }
          gradient="from-accent-amber to-accent-magenta"
        />
        <StatTile
          icon={CheckCircle2}
          label={t.lessonsCompleted}
          value={
            <AnimatedCounter
              end={stats.lessons_completed}
              className="font-display text-3xl font-bold"
            />
          }
          gradient="from-accent-cyan to-primary"
        />
        <StatTile
          icon={Star}
          label={t.level}
          value={
            <AnimatedCounter
              end={stats.level}
              className="font-display text-3xl font-bold"
            />
          }
          gradient="from-accent-magenta to-accent-cyan"
        />
      </div>

      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-8">
        <div className="card-punch rounded-2xl p-6 lg:col-span-5">
          <h2 className="font-display text-xl font-semibold">{t.recentLessons}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{t.recentLessonsDesc}</p>
          <div className="mt-4 space-y-4">
            {recent_lessons.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t.noLessonsYet}</p>
            ) : (
              recent_lessons.map((lesson) => {
                const title =
                  isHe && lesson.title_he ? lesson.title_he : lesson.title;
                // Deep-link to the authored lesson when available; else to
                // the subject-level /learn page for that concept.
                const href = lesson.id
                  ? `/app/lessons/l/${lesson.id}`
                  : `/learn/${lesson.subject}`;
                return (
                  <div key={lesson.concept_id} className="space-y-2">
                    <div className="flex min-w-0 items-center justify-between gap-2">
                      <Link
                        href={href}
                        className="truncate font-medium hover:underline"
                        dir="auto"
                      >
                        {title}
                      </Link>
                      {lesson.est_minutes != null ? (
                        <span className="shrink-0 text-xs text-muted-foreground">
                          {lesson.est_minutes} {t.minutes}
                        </span>
                      ) : null}
                    </div>
                    <Progress
                      value={lesson.progress * 100}
                      className={progressBarClass}
                      aria-label={`${title} progress`}
                    />
                  </div>
                );
              })
            )}
          </div>
        </div>

        <div className="card-punch rounded-2xl p-6 lg:col-span-3">
          <h2 className="font-display text-xl font-semibold">{t.mastery}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{t.masteryDesc}</p>
          <div className="mt-4 space-y-3">
            {mastery_summary.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t.noMasteryYet}</p>
            ) : (
              mastery_summary.map((item) => {
                const name = isHe && item.name_he ? item.name_he : item.name;
                return (
                  <div key={item.concept_id} className="space-y-1.5">
                    <div className="flex min-w-0 items-center justify-between gap-2">
                      <span className="truncate text-sm" dir="auto">
                        {name}
                      </span>
                      <Badge variant={item.score >= 0.7 ? 'success' : 'secondary'}>
                        {Math.round(item.score * 100)}%
                      </Badge>
                    </div>
                    <Progress
                      value={item.score * 100}
                      className={progressBarClass}
                      aria-label={`${name} mastery`}
                    />
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      <section>
        <h2 className="font-display mb-4 text-xl font-semibold">{t.agents}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {dashboardAgents.map(({ agent, emoji, gradientClass }) => (
            <Link
              key={agent}
              href={`/app/chat/${agent}`}
              className="iridescent-border flex flex-col p-5 transition-transform hover:scale-[1.02]"
            >
              <span
                className={cn(
                  'mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br text-xl',
                  gradientClass,
                )}
                aria-hidden
              >
                {emoji}
              </span>
              <h3
                className={cn(
                  'font-display text-lg font-bold bg-gradient-to-r bg-clip-text text-transparent',
                  gradientClass,
                )}
              >
                {agentDisplayNames[agent]}
              </h3>
              <span className="mt-3 text-sm font-medium text-primary">
                {t.startChat} →
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatTile({
  icon: Icon,
  label,
  value,
  gradient,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: ReactNode;
  gradient: string;
}) {
  return (
    <div className="card-punch rounded-2xl p-5">
      <div className="flex items-center gap-3">
        <div
          className={cn(
            'flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br text-primary-foreground',
            gradient,
          )}
        >
          <Icon className="h-5 w-5" aria-hidden />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <div
            className={cn(
              'bg-gradient-to-r bg-clip-text text-transparent',
              gradient,
            )}
          >
            {value}
          </div>
        </div>
      </div>
    </div>
  );
}
