'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import Link from 'next/link';
import { ChevronRight, Clock } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import type { AgentName } from '@asf/schemas/agents';
import type { LearningPlan, PlanConcept } from '@asf/schemas/learning_path';
import { useI18n } from '@/providers/i18n-provider';
import { DueReviewsWidget } from '@/components/due-reviews-widget';
import { currentActiveWeek } from '@/lib/learning-path-types';
import { learnConceptHrefFromProfile } from '@/lib/learn-routes';
import { getSubjectLabel, subjectIcon } from '@/lib/subject-labels';
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
    daysUntilExam: (n: number) => `${n} ימים עד הבגרות`,
    examToday: 'הבגרות היום!',
    streak: (n: number) => `🔥 ${n} ימים רצף`,
    estGrade: (g: number) => `ציון משוער: ~${g}`,
    planTitle: 'התוכנית שלי לשבוע זה',
    noPlanTitle: 'נראה שאין לך תוכנית עדיין — בוא נתחיל!',
    noPlanBlurb: 'השלם את האבחון כדי לקבל תכנית שבועית מותאמת אישית.',
    startNow: 'התחל עכשיו',
    startDiagnostic: 'התחל אבחון',
    browseLearn: 'עבור ללימוד',
    dueReviews: 'חזרה להיום',
    agents: 'הסוכנים שלך',
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
    noPlanTitle: "Looks like you don't have a plan yet — let's get started!",
    noPlanBlurb: 'Complete the diagnostic to get a personalized weekly plan.',
    startNow: 'Start now',
    startDiagnostic: 'Start diagnostic',
    browseLearn: 'Go to Learn',
    dueReviews: 'Due for Review Today',
    agents: 'Your agents',
    statusDone: 'Done',
    statusInProgress: 'In Progress',
    statusNew: 'New',
    minutes: (n: number) => `${n} min`,
  },
} as const;

const AGENT_CARDS: Array<{
  agent: AgentName;
  emoji: string;
  name_he: string;
  name_en: string;
  desc_he: string;
  desc_en: string;
  hoverRing: string;
}> = [
  {
    agent: 'tutor',
    emoji: '🎓',
    name_he: 'מורה',
    name_en: 'Tutor',
    desc_he: 'מדריך עם שאלות — ללמידה עמוקה',
    desc_en: 'Guides with questions — deep understanding',
    hoverRing: 'hover:ring-blue-500/40',
  },
  {
    agent: 'qa_explainer',
    emoji: '💡',
    name_he: 'מסביר',
    name_en: 'Q&A',
    desc_he: 'עונה ישירות מתוך החומר',
    desc_en: 'Direct answers from the curriculum',
    hoverRing: 'hover:ring-green-500/40',
  },
  {
    agent: 'coach',
    emoji: '🏋️',
    name_he: 'מאמן',
    name_en: 'Coach',
    desc_he: 'תרגול יומי ועיוון בחולשות',
    desc_en: 'Daily drills targeting your weak spots',
    hoverRing: 'hover:ring-orange-500/40',
  },
  {
    agent: 'mentor',
    emoji: '🧭',
    name_he: 'מנטור',
    name_en: 'Mentor',
    desc_he: 'מוטיבציה, הרגלים ותכנון',
    desc_en: 'Motivation, habits, and planning',
    hoverRing: 'hover:ring-purple-500/40',
  },
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
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-4 py-1.5 text-sm font-medium text-muted-foreground">
      <span aria-hidden>📈</span>
      {t.estGrade(grade)}
    </span>
  );
}

function PlanItemRow({
  concept,
  isHe,
  pointsGroup,
  subjects,
  isFirst,
}: {
  concept: PlanConcept;
  isHe: boolean;
  pointsGroup?: string | null;
  subjects?: string[] | null;
  isFirst?: boolean;
}) {
  const locale = isHe ? 'he' : 'en';
  const t = STR[locale];
  const href = learnConceptHrefFromProfile(
    concept.concept_id,
    concept.subject,
    pointsGroup,
    subjects,
  );
  const estMinutes = lessonsById.get(concept.concept_id)?.est_minutes;
  const status = masteryStatus(concept.mastery, isHe);
  const emoji = subjectIcon(concept.subject);
  const subjectName = getSubjectLabel(concept.subject, locale);

  return (
    <Link
      href={href}
      className={cn(
        'group flex items-center gap-3 rounded-xl border border-border p-4 transition-all duration-200 hover:border-primary/40 hover:shadow-md',
        isFirst ? 'border-l-4 border-l-primary bg-card' : 'card-punch',
      )}
    >
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xl" aria-hidden>
        {emoji}
      </span>

      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground" dir="auto">
          {conceptDisplayName(concept, isHe)}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">{subjectName}</span>
          {estMinutes != null ? (
            <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" aria-hidden />
              {t.minutes(estMinutes)}
            </span>
          ) : null}
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <Badge variant={status.variant} className="text-xs">
          {status.label}
        </Badge>
        <ChevronRight
          className={cn(
            'h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5',
            isHe && 'rotate-180 group-hover:-translate-x-0.5',
          )}
          aria-hidden
        />
      </div>
    </Link>
  );
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h2 className="font-display mb-4 flex items-center text-xl font-semibold">
      <span className="me-2 inline-block h-2 w-2 rounded-full bg-primary" aria-hidden />
      {children}
    </h2>
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
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];
  const name = firstName(displayName);

  const { subtitle, isExamCountdown } = useMemo(() => {
    if (!nextTestDate) {
      return { subtitle: t.subtitleNoDate, isExamCountdown: false };
    }
    const exam = new Date(nextTestDate);
    const daysLeft = Math.ceil((exam.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (daysLeft <= 0) {
      return { subtitle: t.examToday, isExamCountdown: true };
    }
    return { subtitle: t.daysUntilExam(daysLeft), isExamCountdown: true };
  }, [nextTestDate, t]);

  const week = plan ? currentActiveWeek(plan) : undefined;
  const planItems = (week?.concepts ?? []).slice(0, MAX_PLAN_ITEMS);

  const streakDays = streak?.current_days ?? 0;

  return (
    <div dir={isHe ? 'rtl' : 'ltr'} className="space-y-8">
      {/* Section 1 — Welcome hero */}
      <header className="relative mb-6 overflow-hidden rounded-2xl bg-gradient-to-br from-primary/5 via-background to-accent-magenta/5 p-6">
        <div
          className="absolute -top-8 -right-8 h-32 w-32 rounded-full bg-primary/10 blur-3xl"
          aria-hidden
        />
        <div className="relative space-y-4">
          <h1 className="font-display text-3xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-primary via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
              {t.welcome(name)}
            </span>
          </h1>

          {isExamCountdown ? (
            <span className="inline-flex rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
              {subtitle}
            </span>
          ) : (
            <p className="text-muted-foreground">{subtitle}</p>
          )}

          <div className="flex flex-wrap items-center gap-2">
            {streakDays > 0 ? (
              <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-4 py-1.5 text-sm font-medium">
                <span aria-hidden>🔥</span>
                {isHe ? `${streakDays} ימים רצף` : `${streakDays}-day streak`}
              </span>
            ) : null}
            <EstimatedGradePill isHe={isHe} />
          </div>
        </div>
      </header>

      {/* Section 2 — Learning Plan */}
      <section>
        <SectionHeading>{t.planTitle}</SectionHeading>
        {planItems.length > 0 ? (
          <div className="space-y-3">
            {planItems.map((concept, idx) => (
              <PlanItemRow
                key={concept.concept_id}
                concept={concept}
                isHe={isHe}
                pointsGroup={pointsGroup}
                subjects={subjects}
                isFirst={idx === 0}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/5 to-accent-magenta/5 p-6 text-center">
            <p className="font-display font-medium">{t.noPlanTitle}</p>
            <p className="mt-1 text-sm text-muted-foreground">{t.noPlanBlurb}</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <Button asChild size="sm">
                <Link href="/onboarding">{t.startNow}</Link>
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
        <SectionHeading>{t.agents}</SectionHeading>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {AGENT_CARDS.map(({ agent, emoji, name_he, name_en, desc_he, desc_en, hoverRing }) => (
            <Link
              key={agent}
              href={`/app/chat/${agent}`}
              className={cn(
                'card-punch group flex flex-col gap-2 rounded-xl p-4 transition-all duration-200',
                'hover:scale-[1.01] hover:ring-2',
                hoverRing,
              )}
            >
              <span className="text-2xl" aria-hidden>
                {emoji}
              </span>
              <p className="font-display font-semibold text-foreground">
                {isHe ? name_he : name_en}
              </p>
              <p className="text-xs text-muted-foreground">
                {isHe ? desc_he : desc_en}
              </p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
