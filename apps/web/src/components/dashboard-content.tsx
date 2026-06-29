'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Clock } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { agentDisplayNames, type AgentName } from '@asf/schemas/agents';
import type { LearningPlan, PlanConcept } from '@asf/schemas/learning_path';
import { useI18n } from '@/providers/i18n-provider';
import { DueReviewsWidget } from '@/components/due-reviews-widget';
import { currentActiveWeek } from '@/lib/learning-path-types';
import { learnConceptHrefFromProfile } from '@/lib/learn-routes';
import type { LearnerStreak } from '@/lib/neon-db';
import lessonsIndex from '@/lib/lessons-index.generated.json';

interface LessonIndexEntry {
  id: string;
  est_minutes: number;
}

const lessonsById = new Map(
  (lessonsIndex as LessonIndexEntry[]).map((l) => [l.id, l]),
);

const STR = {
  he: {
    welcome: (name: string) => `ברוך הבא חזרה, ${name}!`,
    subtitleNoDate: 'בוא נלמד משהו חדש היום',
    daysUntilExam: (n: number) => `${n} ימים עד לבגרות`,
    examToday: 'הבגרות היום!',
    streak: (n: number) => `🔥 ${n} ימים רצף`,
    estGrade: (g: number) => `ציון משוער: ~${g}`,
    planTitle: 'התוכנית שלי לשבוע זה',
    noPlanTitle: 'אין עדיין תכנית לשבוע',
    noPlanBlurb: 'השלם את האבחון או התחל ללמוד כדי לקבל תכנית שבועית מותאמת.',
    startDiagnostic: 'התחל אבחון',
    browseLearn: 'עבור ללימוד',
    dueReviews: 'חזרה להיום',
    agents: 'הסוכנים שלך',
    goToExams: '→ כניסה לאזור הבחינות',
    statusDone: 'הושלם',
    statusInProgress: 'בתהליך',
    statusNew: 'חדש',
    minutes: (n: number) => `${n} דק׳`,
  },
  en: {
    welcome: (name: string) => `Welcome back, ${name}!`,
    subtitleNoDate: "Let's learn something new today",
    daysUntilExam: (n: number) => `${n} days until exam`,
    examToday: 'Exam day!',
    streak: (n: number) => `🔥 ${n}-day streak`,
    estGrade: (g: number) => `Est. grade: ~${g}`,
    planTitle: 'My Plan for This Week',
    noPlanTitle: 'No weekly plan yet',
    noPlanBlurb: 'Complete the diagnostic or start learning to get a personalized weekly plan.',
    startDiagnostic: 'Start diagnostic',
    browseLearn: 'Go to Learn',
    dueReviews: 'Due for Review Today',
    agents: 'Your agents',
    goToExams: '→ Go to Practice Tests',
    statusDone: 'Done',
    statusInProgress: 'In Progress',
    statusNew: 'New',
    minutes: (n: number) => `${n} min`,
  },
} as const;

const COMPACT_AGENTS: Array<{ agent: AgentName; emoji: string }> = [
  { agent: 'tutor', emoji: '📚' },
  { agent: 'coach', emoji: '💪' },
  { agent: 'qa_explainer', emoji: '💡' },
  { agent: 'mentor', emoji: '🌟' },
];

const MAX_PLAN_ITEMS = 5;

function firstName(displayName: string): string {
  const trimmed = displayName.trim();
  if (!trimmed) return displayName;
  return trimmed.split(/\s+/)[0] ?? trimmed;
}

function masteryStatus(
  mastery: number | null | undefined,
  isHe: boolean,
): { label: string; variant: 'success' | 'warning' | 'secondary' } {
  const t = STR[isHe ? 'he' : 'en'];
  if (mastery == null || mastery === 0) {
    return { label: t.statusNew, variant: 'secondary' };
  }
  if (mastery >= 0.7) {
    return { label: t.statusDone, variant: 'success' };
  }
  return { label: t.statusInProgress, variant: 'warning' };
}

function conceptDisplayName(concept: PlanConcept, isHe: boolean): string {
  if (isHe && concept.name_he?.trim()) return concept.name_he;
  return concept.name;
}

function EstimatedGradePill({ isHe }: { isHe: boolean }) {
  const [grade, setGrade] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetch('/api/progress/estimated-grade')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (cancelled || !data) return;
        const avg = Number(data.masteryAvg ?? 0);
        const est = data.estimatedGrade;
        if (typeof est === 'number' && avg >= 0.3) setGrade(est);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  if (grade == null) return null;

  const t = STR[isHe ? 'he' : 'en'];
  return (
    <span className="inline-flex items-center rounded-full border border-border bg-surface-2/60 px-3 py-1 text-sm text-muted-foreground">
      {t.estGrade(grade)}
    </span>
  );
}

function PlanItemRow({
  concept,
  isHe,
  pointsGroup,
  subjects,
}: {
  concept: PlanConcept;
  isHe: boolean;
  pointsGroup?: string | null;
  subjects?: string[] | null;
}) {
  const t = STR[isHe ? 'he' : 'en'];
  const href = learnConceptHrefFromProfile(
    concept.concept_id,
    concept.subject,
    pointsGroup,
    subjects,
  );
  const estMinutes = lessonsById.get(concept.concept_id)?.est_minutes;
  const status = masteryStatus(concept.mastery, isHe);

  return (
    <Link
      href={href}
      className="flex items-center justify-between gap-3 rounded-xl border border-border/60 bg-surface-1/40 px-4 py-3 transition-colors hover:border-primary/40 hover:bg-surface-2/40"
    >
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground" dir="auto">
          {conceptDisplayName(concept, isHe)}
        </p>
        {estMinutes != null ? (
          <p className="mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" aria-hidden />
            {t.minutes(estMinutes)}
          </p>
        ) : null}
      </div>
      <Badge variant={status.variant} className="shrink-0 text-xs">
        {status.label}
      </Badge>
    </Link>
  );
}

export function DashboardContent({
  displayName,
  plan,
  nextTestDate,
  streak,
  pointsGroup,
  subjects,
}: {
  displayName: string;
  plan: LearningPlan | null;
  nextTestDate?: string | null;
  streak?: LearnerStreak;
  pointsGroup?: string | null;
  subjects?: string[] | null;
}) {
  const { messages, locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];
  const name = firstName(displayName);

  const subtitle = useMemo(() => {
    if (!nextTestDate) return t.subtitleNoDate;
    const exam = new Date(nextTestDate);
    const daysLeft = Math.ceil((exam.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (daysLeft <= 0) return t.examToday;
    return t.daysUntilExam(daysLeft);
  }, [nextTestDate, t]);

  const week = plan ? currentActiveWeek(plan) : undefined;
  const planItems = (week?.concepts ?? []).slice(0, MAX_PLAN_ITEMS);

  const streakDays = streak?.current_days ?? 0;

  return (
    <div dir={isHe ? 'rtl' : 'ltr'} className="space-y-8">
      {/* Section 1 — Welcome */}
      <header>
        <h1 className="font-display text-3xl font-bold tracking-tight text-foreground">
          {t.welcome(name)}
        </h1>
        <p className="mt-1 text-muted-foreground">{subtitle}</p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {streakDays > 0 ? (
            <span className="inline-flex items-center rounded-full border border-border bg-surface-2/60 px-3 py-1 text-sm">
              {t.streak(streakDays)}
            </span>
          ) : null}
          <EstimatedGradePill isHe={isHe} />
        </div>
        <Link
          href="/app/exams"
          className="mt-3 inline-block text-sm text-muted-foreground transition-colors hover:text-primary"
        >
          {t.goToExams}
        </Link>
      </header>

      {/* Section 2 — Learning Plan */}
      <section>
        <h2 className="font-display mb-4 text-xl font-semibold">{t.planTitle}</h2>
        {planItems.length > 0 ? (
          <div className="space-y-2">
            {planItems.map((concept) => (
              <PlanItemRow
                key={concept.concept_id}
                concept={concept}
                isHe={isHe}
                pointsGroup={pointsGroup}
                subjects={subjects}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-border/60 bg-surface-1/40 p-6 text-center">
            <p className="font-medium">{t.noPlanTitle}</p>
            <p className="mt-1 text-sm text-muted-foreground">{t.noPlanBlurb}</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <Button asChild size="sm">
                <Link href="/diagnostic">{t.startDiagnostic}</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/learn">{t.browseLearn}</Link>
              </Button>
            </div>
          </div>
        )}
      </section>

      {/* Section 3 — Due Reviews (conditional) */}
      <DueReviewsWidget sectionTitle={t.dueReviews} hideTitle />

      {/* Section 4 — Compact Agents */}
      <section>
        <h2 className="font-display mb-3 text-xl font-semibold">{t.agents}</h2>
        <div className="flex flex-wrap gap-2">
          {COMPACT_AGENTS.map(({ agent, emoji }) => (
            <Link
              key={agent}
              href={`/app/chat/${agent}`}
              className={cn(
                'inline-flex items-center gap-2 rounded-xl border border-border/60',
                'bg-surface-1/40 px-4 py-2.5 text-sm font-medium transition-colors',
                'hover:border-primary/40 hover:bg-surface-2/40',
              )}
            >
              <span aria-hidden>{emoji}</span>
              {(messages.dashboard.agentNames as Record<string, string>)?.[agent] ??
                agentDisplayNames[agent]}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
