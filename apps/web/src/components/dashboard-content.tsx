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
import { TeacherChip } from '@/components/teacher-chip';
import { currentActiveWeek } from '@/lib/learning-path-types';
import { examPrepContext } from '@/lib/exam-prep';
import { ExamPrepQuizBanner } from '@/components/exam-prep-quiz-banner';
import { learnConceptHrefFromProfile } from '@/lib/learn-routes';
import { getSubjectLabel, subjectIcon } from '@/lib/subject-labels';
import { pickConceptTitle, resolveConceptTitles } from '@/lib/concept-display-names';
import { goalCountdownLabel, isBagrutTrack } from '@/lib/goal-track';
import type { LearnerStreak } from '@/lib/neon-db';
import { agentAccentVars } from '@/lib/design-tokens';
import { WeekTrainingCard, type ClientWeekTrainingSpec } from '@/components/week-training-card';
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
    makhinaCue: 'המסע שלך לאוניברסיטה',
    daysUntilExam: (n: number) => `${n} ימים עד הבגרות`,
    daysUntilGoal: (n: number) => `${n} ימים עד יעד הלימוד`,
    examToday: 'הבגרות היום!',
    goalToday: 'יום היעד!',
    viewFullPlan: 'צפה בתוכנית המלאה →',
    streak: (n: number) => `🔥 ${n} ימים רצף`,
    estGrade: (g: number) => `ציון משוער: ~${g}`,
    readinessPct: (p: number) => `מוכנות ליעד: ~${p}%`,
    kindTrain: 'אימון',
    kindRest: 'מנוחה',
    planTitle: 'התוכנית שלי לשבוע זה',
    noPlanTitle: 'נראה שאין לך תוכנית עדיין — בוא נתחיל!',
    noPlanBlurb: 'השלם/י את שאלון ההיכרות כדי לקבל תכנית שבועית — או גלשו בלימוד בינתיים.',
    noPlanBlurbHasProfile: 'צרו תוכנית שבועית מהמטרות שכבר מילאתם — או גלשו בלימוד בינתיים.',
    startNow: 'התחל/י עכשיו',
    createPlan: 'צור/י תוכנית',
    browseLearn: 'עבור ללימוד',
    dueReviews: 'חזרה להיום',
    agents: 'הסוכנים שלך',
    statusDone: 'הושלם',
    statusInProgress: 'בתהליך',
    statusNew: 'חדש',
    actionStart: 'התחל',
    actionContinue: 'המשך',
    minutes: (n: number) => `${n} דק׳`,
    // R4 — Overflow honesty notice
    overflowTitle: 'לא ייכנס עד היעד',
    overflowBody: (names: string) =>
      `${names} — הרחיבו את היעד או הוסיפו שעות לימוד`,
    overflowCta: 'דברו עם המורה',
    // R5 — Post-goal re-plan CTA
    replanTitle: 'התוכנית הסתיימה',
    replanBody: 'התוכנית שלך הגיעה לסיומה. זה הזמן ליצור תוכנית חדשה בהתאם להתקדמות שלך.',
    replanCta: 'תכנן מחדש',
    nextWeekLocked: 'שבוע 2 ייפתח לאחר השלמת שבוע 1',
  },
  en: {
    welcome: (name: string) => `Welcome back, ${name}!`,
    subtitleNoDate: "Let's learn something new today",
    makhinaCue: 'Your university prep journey',
    daysUntilExam: (n: number) => `${n} days until exam`,
    daysUntilGoal: (n: number) => `${n} days until your goal`,
    examToday: 'Exam day!',
    goalToday: 'Goal day!',
    viewFullPlan: 'View full plan →',
    streak: (n: number) => `🔥 ${n}-day streak`,
    estGrade: (g: number) => `Est. grade: ~${g}`,
    readinessPct: (p: number) => `Goal readiness: ~${p}%`,
    kindTrain: 'Practice',
    kindRest: 'Rest',
    planTitle: 'My Plan for This Week',
    noPlanTitle: "Looks like you don't have a plan yet — let's get started!",
    noPlanBlurb: 'Complete onboarding to get a weekly plan — or browse Learn in the meantime.',
    noPlanBlurbHasProfile: 'Create a weekly plan from the goals you already shared — or browse Learn.',
    startNow: 'Start now',
    createPlan: 'Create my plan',
    browseLearn: 'Go to Learn',
    dueReviews: 'Due for Review Today',
    agents: 'Your agents',
    statusDone: 'Done',
    statusInProgress: 'In Progress',
    statusNew: 'New',
    actionStart: 'Start',
    actionContinue: 'Continue',
    minutes: (n: number) => `${n} min`,
    // R4 — Overflow honesty notice
    overflowTitle: "Won't fit before your goal",
    overflowBody: (names: string) =>
      `${names} — extend your goal date or add more study hours`,
    overflowCta: 'Talk to your Tutor',
    // R5 — Post-goal re-plan CTA
    replanTitle: 'Plan ended',
    replanBody: "Your plan has reached its end date. It's time to create a new plan based on your progress.",
    replanCta: 'Re-plan',
    nextWeekLocked: 'Week 2 unlocks after you complete Week 1',
  },
} as const;

const AGENT_CARDS: Array<{
  agent: AgentName;
  emoji: string;
  name_he: string;
  name_en: string;
  desc_he: string;
  desc_en: string;
}> = [
  {
    agent: 'tutor',
    emoji: '🎓',
    name_he: 'מורה',
    name_en: 'Tutor',
    desc_he: 'מדריך עם שאלות — ללמידה עמוקה ותשובות ישירות',
    desc_en: 'Socratic guidance and cited Q&A from the corpus',
  },
  {
    agent: 'mentor',
    emoji: '🧭',
    name_he: 'מנטור',
    name_en: 'Mentor',
    desc_he: 'מוטיבציה, הרגלים ותכנון',
    desc_en: 'Motivation, habits, and planning',
  },
  {
    agent: 'coach',
    emoji: '🏋️',
    name_he: 'מאמן',
    name_en: 'Coach',
    desc_he: 'תרגול יומי וחיזוק בחולשות',
    desc_en: 'Daily drills targeting your weak spots',
  },
  {
    agent: 'reviewer',
    emoji: '📝',
    name_he: 'מבקר',
    name_en: 'Reviewer',
    desc_he: 'משוב מפורט על עבודות ופתרונות',
    desc_en: 'Rubric-first feedback on your work',
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
  locale: 'he' | 'en',
): { label: string; variant: 'success' | 'warning' | 'secondary' } {
  const t = STR[locale];
  if (mastery == null || mastery === 0) {
    return { label: t.actionStart, variant: 'secondary' };
  }
  if (mastery >= 0.7) {
    return { label: t.statusDone, variant: 'success' };
  }
  return { label: t.actionContinue, variant: 'warning' };
}

function conceptDisplayName(concept: PlanConcept, locale: 'he' | 'en'): string {
  const titles = resolveConceptTitles(concept.concept_id, {
    title_en: concept.name,
    title_he: concept.name_he ?? null,
  });
  return pickConceptTitle(titles, locale);
}

function resolvePlanSubject(
  conceptSubject: string,
  subjects?: string[] | null,
  pointsGroup?: string | null,
): string {
  if (conceptSubject !== 'math' && conceptSubject !== 'physics') {
    return conceptSubject;
  }
  const enrolled = subjects ?? [];
  if (enrolled.length === 1) return enrolled[0]!;
  const specific = enrolled.find(
    (s) => s.includes('math') || s.includes('physics') || s === 'makhina' || s === 'university_prep',
  );
  if (specific) return specific;
  if (pointsGroup === 'makhina') return 'makhina';
  return conceptSubject;
}

function EstimatedGradePill({ isHe, onGradient = false }: { isHe: boolean; onGradient?: boolean }) {
  const [label, setLabel] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetch('/api/progress/estimated-grade')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (cancelled || !data) return;
        const avg = Number(data.masteryAvg ?? 0);
        const metric = typeof data.metric === 'string' ? data.metric : 'estimated_grade';
        const est = data.estimatedGrade;
        if (typeof est !== 'number') return;
        const t = STR[isHe ? 'he' : 'en'];
        if (metric === 'goal_readiness') {
          const pct =
            typeof data.readinessPct === 'number' ? data.readinessPct : Math.round(est);
          setLabel(t.readinessPct(pct));
          return;
        }
        if (avg >= 0.3) setLabel(t.estGrade(est));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [isHe]);

  if (label == null) return null;

  return (
    <span
      className={cn(
        'flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-medium',
        onGradient
          ? 'bg-white/15 text-white backdrop-blur-sm'
          : 'border border-border bg-card text-muted-foreground',
      )}
    >
      <span aria-hidden>📈</span>
      {label}
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
  const kind = concept.kind ?? 'lesson';
  const href =
    kind === 'train'
      ? `/app/practice?concept=${encodeURIComponent(concept.concept_id)}`
      : kind === 'rest'
        ? '/app/plan'
        : learnConceptHrefFromProfile(
            concept.concept_id,
            concept.subject,
            pointsGroup,
            subjects,
          );
  const estMinutes = lessonsById.get(concept.concept_id)?.est_minutes;
  const status = masteryStatus(concept.mastery, locale);
  const emoji = subjectIcon(concept.subject);
  const subjectSlug = resolvePlanSubject(concept.subject, subjects, pointsGroup);
  const subjectName = getSubjectLabel(subjectSlug, locale);

  return (
    <Link
      href={href}
      className={cn(
        'group flex items-center gap-3 rounded-xl p-4 transition-all duration-200 hover:scale-[1.01]',
        isFirst ? 'iridescent-border ring-2 ring-primary/40' : 'card-punch shadow-sm',
      )}
    >
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xl" aria-hidden>
        {emoji}
      </span>

      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground" dir="auto">
          {conceptDisplayName(concept, locale)}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">{subjectName}</span>
          {kind === 'train' ? (
            <Badge variant="outline" className="text-xs">
              {t.kindTrain}
            </Badge>
          ) : null}
          {kind === 'rest' ? (
            <Badge variant="secondary" className="text-xs">
              {t.kindRest}
            </Badge>
          ) : null}
          {estMinutes != null && kind === 'lesson' ? (
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

function SectionHeading({
  children,
  accent = 'primary',
}: {
  children: ReactNode;
  accent?: 'primary' | 'cyan';
}) {
  return (
    <h2 className="font-display mb-4 flex items-center gap-2.5 text-xl font-semibold text-foreground">
      <span
        className={cn(
          'h-5 w-1 rounded-full',
          accent === 'cyan' ? 'bg-accent-cyan' : 'bg-primary',
        )}
        aria-hidden
      />
      {children}
    </h2>
  );
}

function isMakhinaFocus(
  pointsGroup?: string | null,
  subjects?: string[] | null,
  goal?: string | null,
): boolean {
  if (pointsGroup === 'makhina') return true;
  if (goal === 'makhina' || goal === 'university_prep') return true;
  return (
    subjects?.some(
      (s) => s === 'makhina' || s.includes('makhina') || s === 'university_prep',
    ) ?? false
  );
}

/**
 * R4: Bilingual overflow-honesty notice.
 * Shown below the plan section when the BFS engine cut concepts that didn't
 * fit the learner's horizon × capacity. Purely informational — one restrained
 * card, no alarmist language, with a CTA to /plan-setup to update the goal.
 */
function OverflowNotice({
  overflowConceptIds,
  isHe,
}: {
  overflowConceptIds: string[];
  isHe: boolean;
}) {
  const t = STR[isHe ? 'he' : 'en'];
  const locale = isHe ? 'he' : 'en';
  if (overflowConceptIds.length === 0) return null;

  const names = overflowConceptIds
    .slice(0, 5)
    .map((id) => {
      const titles = resolveConceptTitles(id, null);
      return pickConceptTitle(titles, locale);
    })
    .join(', ');
  const moreCount = overflowConceptIds.length - 5;
  const displayNames = moreCount > 0 ? `${names} +${moreCount}` : names;

  return (
    <div
      dir={isHe ? 'rtl' : 'ltr'}
      className="rounded-xl border border-amber-300/60 bg-amber-50/60 px-4 py-3 text-sm dark:border-amber-500/30 dark:bg-amber-900/10"
      role="note"
      aria-label={t.overflowTitle}
    >
      <span className="font-semibold text-amber-700 dark:text-amber-400">
        {t.overflowTitle}:{' '}
      </span>
      <span className="text-muted-foreground">{t.overflowBody(displayNames)}</span>
      {/* Goal editing happens in Tutor chat — /plan-setup has no goal UI. */}
      <Link
        href="/app/chat/tutor"
        className="ms-2 font-medium text-primary hover:underline"
      >
        {t.overflowCta} →
      </Link>
    </div>
  );
}

/**
 * R5: Bilingual post-goal re-plan CTA.
 * Shown when plan.needs_replan === true (today > plan.end_date).
 * Routes to /plan-setup — does NOT auto-regenerate.
 */
function ReplanBanner({ isHe }: { isHe: boolean }) {
  const t = STR[isHe ? 'he' : 'en'];
  return (
    <div
      dir={isHe ? 'rtl' : 'ltr'}
      className="rounded-xl border border-primary/30 bg-gradient-to-br from-primary/5 to-accent-magenta/5 p-5 shadow-sm"
      role="alert"
    >
      <p className="font-display font-semibold text-foreground">{t.replanTitle}</p>
      <p className="mt-1 text-sm text-muted-foreground">{t.replanBody}</p>
      {/* ?replan=1 makes /plan-setup skip its plan-exists shortcut (the expired
          plan is still status='active') and force a fresh bootstrap. */}
      <Button asChild size="sm" className="mt-3">
        <Link href="/plan-setup?replan=1">{t.replanCta}</Link>
      </Button>
    </div>
  );
}

export function DashboardContent({
  displayName,
  plan,
  nextTestDate,
  finalGoalDate,
  streak,
  pointsGroup,
  subjects,
  goal,
  goalKey,
  teacher,
  weekSpec,
  hasProfile = false,
}: {
  displayName: string;
  plan: LearningPlan | null;
  nextTestDate?: string | null;
  finalGoalDate?: string | null;
  streak?: LearnerStreak;
  pointsGroup?: string | null;
  subjects?: string[] | null;
  goal?: string | null;
  goalKey?: string | null;
  teacher?: { real_name: string; username: string } | null;
  weekSpec?: ClientWeekTrainingSpec | null;
  hasProfile?: boolean;
}) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];
  const name = firstName(displayName);

  const { subtitle, isExamCountdown } = useMemo(() => {
    const countdownDate =
      finalGoalDate &&
      (!nextTestDate ||
        new Date(finalGoalDate).getTime() > new Date(nextTestDate).getTime())
        ? finalGoalDate
        : nextTestDate;

    if (!countdownDate) {
      return { subtitle: goal ?? t.subtitleNoDate, isExamCountdown: false };
    }
    const target = new Date(countdownDate);
    const daysLeft = Math.ceil((target.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    const bagrut = isBagrutTrack({ goalKey, goal });
    return {
      subtitle: goalCountdownLabel(isHe ? 'he' : 'en', daysLeft, { isBagrut: bagrut }),
      isExamCountdown: true,
    };
  }, [nextTestDate, finalGoalDate, goal, goalKey, isHe, t]);

  const week = plan ? currentActiveWeek(plan) : undefined;
  const planItems = (week?.concepts ?? []).slice(0, MAX_PLAN_ITEMS);
  const nextWeekEmpty =
    !!week &&
    !(plan?.weeks ?? []).find(
      (w) => w.week_number === week.week_number + 1 && w.concepts.length > 0,
    );
  const examPrep = useMemo(
    () => examPrepContext(plan, nextTestDate, finalGoalDate),
    [plan, nextTestDate, finalGoalDate],
  );

  const streakDays = streak?.current_days ?? 0;
  const showMakhinaCue = isMakhinaFocus(pointsGroup, subjects, goal);

  return (
    <div dir={isHe ? 'rtl' : 'ltr'} className="space-y-8">
      {/* Section 1 — Welcome hero */}
      <header className="relative mb-6 overflow-hidden rounded-2xl bg-primary p-6 shadow-md md:p-8">
        <div className="bg-grain pointer-events-none absolute inset-0" aria-hidden />
        <div
          className="pointer-events-none absolute inset-0 opacity-50"
          style={{
            backgroundImage:
              'radial-gradient(at 15% 20%, hsl(32 68% 55% / 0.35), transparent 55%), radial-gradient(at 85% 90%, hsl(12 55% 55% / 0.3), transparent 55%)',
          }}
          aria-hidden
        />
        <div className="relative space-y-4 text-primary-foreground">
          <h1 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            {t.welcome(name)}
          </h1>

          {showMakhinaCue ? (
            <p className="text-sm font-medium text-white/90">{t.makhinaCue}</p>
          ) : null}

          {isExamCountdown ? (
            <span className="inline-flex rounded-full bg-white/20 px-4 py-1.5 text-sm font-semibold backdrop-blur-sm">
              {subtitle}
            </span>
          ) : (
            <p className="text-white/80">{subtitle}</p>
          )}

          {subjects?.includes('makhina') || pointsGroup === 'makhina' ? (
            <p className="text-sm text-white/75" dir={isHe ? 'rtl' : 'ltr'}>
              {isHe ? 'המסע שלך לאוניברסיטה 🎓' : 'Your university prep journey 🎓'}
            </p>
          ) : null}

          <div className="flex flex-wrap items-center gap-3 pt-1">
            {teacher ? (
              <TeacherChip realName={teacher.real_name} username={teacher.username} />
            ) : null}
            {streakDays > 0 ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-4 py-2 text-sm font-medium backdrop-blur-sm">
                <span aria-hidden>🔥</span>
                {isHe ? `${streakDays} ימים רצף` : `${streakDays}-day streak`}
              </span>
            ) : null}
            <EstimatedGradePill isHe={isHe} onGradient />
          </div>
        </div>
      </header>

      {examPrep ? <ExamPrepQuizBanner ctx={examPrep} /> : null}

      {/* R5 — Post-goal re-plan CTA (shown when plan has expired) */}
      {plan?.needs_replan ? <ReplanBanner isHe={isHe} /> : null}

      {/* Section 2 — Learning Plan */}
      <section className="rounded-2xl border border-border bg-card p-5 shadow-sm md:p-6">
        <SectionHeading accent="cyan">{t.planTitle}</SectionHeading>
        {planItems.length > 0 ? (
          <div className="space-y-3">
            {goal ? (
              <p className="text-sm text-muted-foreground" dir="auto">
                {goal}
              </p>
            ) : null}
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
            {/* R4 — Overflow honesty: show concepts that didn't fit the horizon */}
            {(plan?.overflow_concepts?.length ?? 0) > 0 ? (
              <OverflowNotice
                overflowConceptIds={plan!.overflow_concepts!}
                isHe={isHe}
              />
            ) : null}
            <Link
              href="/app/plan"
              className="inline-block text-sm font-medium text-primary hover:underline"
            >
              {t.viewFullPlan}
            </Link>
            {nextWeekEmpty ? (
              <p className="text-xs text-muted-foreground" dir="auto">
                {t.nextWeekLocked}
              </p>
            ) : null}
          </div>
        ) : (
          <div className="rounded-xl border border-primary/20 bg-gradient-to-br from-primary/5 to-accent-magenta/5 p-6 text-center">
            <p className="font-display font-medium">{t.noPlanTitle}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {hasProfile ? t.noPlanBlurbHasProfile : t.noPlanBlurb}
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {hasProfile ? (
                <Button asChild size="sm">
                  <Link href="/plan-setup">{t.createPlan}</Link>
                </Button>
              ) : (
                <Button asChild size="sm">
                  <Link href="/onboarding">{t.startNow}</Link>
                </Button>
              )}
              <Button asChild variant="outline" size="sm">
                <Link href="/learn">{t.browseLearn}</Link>
              </Button>
            </div>
          </div>
        )}
      </section>

      {/* Section 3 — This week's training (derived spec — routes into existing surfaces) */}
      {weekSpec ? <WeekTrainingCard spec={weekSpec} /> : null}

      {/* Section 4 — Due Reviews (conditional) */}
      <DueReviewsWidget sectionTitle={t.dueReviews} hideTitle />

      {/* Section 5 — Compact Agents */}
      <section className="rounded-2xl border border-border bg-card p-5 shadow-sm md:p-6">
        <SectionHeading>{t.agents}</SectionHeading>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {AGENT_CARDS.map(({ agent, emoji, name_he, name_en, desc_he, desc_en }) => (
            <Link
              key={agent}
              href={`/app/chat/${agent}`}
              style={agentAccentVars(agent)}
              className="card-punch agent-accent-card group flex flex-col gap-2 rounded-xl p-4"
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
