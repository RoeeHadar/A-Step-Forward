'use client';

import Link from 'next/link';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Button } from '@asf/ui/button';
import type { LearningPlan, PlanConcept } from '@asf/schemas/learning_path';
import { currentActiveWeek } from '@/lib/learning-path-types';
import { examPrepContext } from '@/lib/exam-prep';
import { ExamPrepQuizBanner } from '@/components/exam-prep-quiz-banner';
import { learnConceptHrefFromProfile } from '@/lib/learn-routes';
import { getSubjectLabel, subjectIcon } from '@/lib/subject-labels';
import { pickConceptTitle, resolveConceptTitles } from '@/lib/concept-display-names';
import { useLanguagePreference, type Lang } from '@/hooks/use-language-preference';

/**
 * The learner's current weekly plan, rendered fully bilingual.
 *
 * Hebrew is the default UI on this platform (`useLanguagePreference('he')`).
 * Concept display names prefer `concept.name_he` when language is `he` and
 * fall through to `concept.name` (English) when no Hebrew name is available
 * for that concept. Mastery percentages and progress bars are language-agnostic.
 *
 * Subjects (`math` / `physics`) get a tiny localised label map. Anything else
 * (e.g. the free-text `plan.goal` the learner wrote during onboarding) is
 * shown verbatim — `dir="auto"` lets the browser pick a sensible direction
 * per string.
 */

const STR = {
  he: {
    title: 'תכנית הלימוד שלך',
    week: (n: number) => `שבוע ${n}`,
    week_status: (n: number, status: string) => `${n} מושגים · סטטוס: ${statusHe(status)}`,
    start_week_quiz: 'התחל מבחן שבועי',
    all_weeks: 'כל השבועות',
    future_weeks: 'שבועות עתידיים (עשויים להשתנות לפי התקדמות)',
    week_chip: (n: number, c: number) => `שבוע ${n}: ${c} מושגים`,
    no_weeks: 'אין עדיין שבועות בתכנית.',
    progress: 'התקדמות',
    sections_label: 'סעיפים בספר',
    browse_subject: (s: string, lang: Lang) => `עיין בתכני ${getSubjectLabel(s, lang)}`,
    not_assessed: 'טרם הוערך',
    mastery_pct: (p: number) => `${p}% שליטה`,
    kindTrain: 'אימון',
    kindRest: 'מנוחה',
    target_date: (d: string) => `יעד: ${d}`,
    plan_horizon: (start: string, end: string) => `תקופת התוכנית: ${start} – ${end}`,
    week_until: (d: string) => `עד ${d}`,
    projected_note:
      'השבועות הבאים עשויים להשתנות לפי ציונים, מבחנים והתקדמות בפועל.',
    readiness_title: 'מוכנות ליעד',
    readiness_pct: (p: number) => `${p}% מוכנות`,
    pace_ahead: 'מקדים/ה את הקצב',
    pace_on_track: 'בקצב הנכון',
    pace_at_risk: 'מאחור מול היעד',
    concepts_left: (n: number) => `נותרו ${n} מושגים ליעד`,
    weeks_to_goal: (n: number) => `~${n} שבועות ליעד`,
    readiness_humble: 'המספר הוא כלי בלבד — הוא לא מבטיח הצלחה. המשיכו להתאמן עד יום המבחן.',
    readiness_final_phase: 'שלב אחרון: התמקדו בסימולציות מלאות ובחזרה ממוקדת על נקודות התורפה.',
    readiness_day_before:
      'יום לפני המבחן: רק חזרה על התיאוריה ושיחה עם המנטור להרגעה — בלי חומר חדש.',
    readiness_exam_ready: 'אתם קרובים מאוד — אבל אי אפשר להבטיח תוצאה. המשיכו לתרגל עד הסוף.',
    readiness_needs_mock: 'כדי להעלות את המוכנות — עברו סימולציה מלאה בתנאי מבחן.',
  },
  en: {
    title: 'Your learning plan',
    week: (n: number) => `Week ${n}`,
    week_status: (n: number, status: string) => `${n} concepts · ${statusEn(status)}`,
    start_week_quiz: 'Start Week Quiz',
    all_weeks: 'All weeks',
    future_weeks: 'Upcoming weeks (may shift based on your progress)',
    week_chip: (n: number, c: number) => `Week ${n}: ${c} concepts`,
    no_weeks: 'No weeks in this plan yet.',
    progress: 'Progress',
    sections_label: 'Textbook sections',
    browse_subject: (s: string, lang: Lang) => `Browse ${getSubjectLabel(s, lang)} content`,
    not_assessed: 'Not assessed',
    mastery_pct: (p: number) => `${p}% mastery`,
    kindTrain: 'Practice',
    kindRest: 'Rest',
    target_date: (d: string) => `Target: ${d}`,
    plan_horizon: (start: string, end: string) => `Plan period: ${start} – ${end}`,
    week_until: (d: string) => `Through ${d}`,
    projected_note:
      'This is a projected plan — upcoming weeks may change based on quizzes and mastery.',
    readiness_title: 'Goal readiness',
    readiness_pct: (p: number) => `${p}% ready`,
    pace_ahead: 'Ahead of pace',
    pace_on_track: 'On track',
    pace_at_risk: 'Behind pace',
    concepts_left: (n: number) => `${n} concepts left to goal`,
    weeks_to_goal: (n: number) => `~${n} weeks to goal`,
    readiness_humble:
      'This number is only a tool — it cannot promise success. Keep practicing until exam day.',
    readiness_final_phase:
      'Final phase: focus on full mock exams and targeted review of your weak spots.',
    readiness_day_before:
      'Day before the exam: just a theory review and a calming talk with your Mentor — no new material.',
    readiness_exam_ready:
      "You're very close — but no one can guarantee a result. Keep practicing to the end.",
    readiness_needs_mock: 'To raise your readiness, sit a full mock exam under exam conditions.',
  },
} as const;

const STATUS_HE: Record<string, string> = {
  active: 'פעיל',
  upcoming: 'עתידי',
  completed: 'הושלם',
  skipped: 'דולג',
};

const STATUS_EN: Record<string, string> = {
  active: 'in progress',
  upcoming: 'upcoming',
  completed: 'done',
  skipped: 'skipped',
};

function statusHe(status: string): string {
  return STATUS_HE[status.toLowerCase()] ?? status;
}

function statusEn(status: string): string {
  return STATUS_EN[status.toLowerCase()] ?? status;
}

function masteryBadgeVariant(score: number | null | undefined): 'success' | 'warning' | 'secondary' {
  if (score == null) return 'secondary';
  if (score > 0.7) return 'success';
  if (score >= 0.4) return 'warning';
  return 'secondary';
}

function masteryLabel(score: number | null | undefined, lang: Lang): string {
  const t = STR[lang];
  if (score == null) return t.not_assessed;
  return t.mastery_pct(Math.round(score * 100));
}

function displayName(concept: PlanConcept, lang: Lang): string {
  const titles = resolveConceptTitles(concept.concept_id, {
    title_en: concept.name,
    title_he: concept.name_he ?? null,
  });
  return pickConceptTitle(titles, lang);
}

function ConceptCard({ concept, lang }: { concept: PlanConcept; lang: Lang }) {
  const t = STR[lang];
  const isHe = lang === 'he';
  const kind = concept.kind ?? 'lesson';
  const mastery = concept.mastery ?? 0;
  const progressPct = Math.round(mastery * 100);
  const name = displayName(concept, lang);
  const href =
    kind === 'train'
      ? `/app/practice?concept=${encodeURIComponent(concept.concept_id)}`
      : kind === 'rest'
        ? '/app/plan'
        : learnConceptHrefFromProfile(concept.concept_id, concept.subject);
  const emoji = subjectIcon(concept.subject);
  const subjectName = getSubjectLabel(concept.subject, lang);

  return (
    <Link href={href} className="block transition-opacity hover:opacity-90">
    <Card className="glass-surface border-border/60" dir={isHe ? 'rtl' : 'ltr'}>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="flex min-w-0 items-start gap-2">
            <span className="text-lg" aria-hidden>{emoji}</span>
            <div className="min-w-0">
              <CardTitle className="text-base" dir="auto">
                {name}
              </CardTitle>
              <div className="mt-0.5 flex flex-wrap items-center gap-2">
                <p className="text-xs text-muted-foreground">{subjectName}</p>
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
              </div>
            </div>
          </div>
          {kind === 'lesson' ? (
            <Badge variant={masteryBadgeVariant(concept.mastery)}>
              {masteryLabel(concept.mastery, lang)}
            </Badge>
          ) : null}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {kind === 'lesson' ? (
        <div>
          <div className="mb-1 flex justify-between text-xs text-muted-foreground">
            <span>{t.progress}</span>
            <span>{progressPct}%</span>
          </div>
          <div className="h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${progressPct}%` }}
              role="progressbar"
              aria-valuenow={progressPct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${name} ${t.progress.toLowerCase()}`}
            />
          </div>
        </div>
        ) : null}

        {kind === 'lesson' && concept.suggested_sections.length > 0 ? (
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">
              {t.sections_label}
            </p>
            <ul className="space-y-1">
              {concept.suggested_sections.slice(0, 3).map((section) => (
                <li key={section.id}>
                  <span
                    className="text-sm text-primary"
                    dir="auto"
                  >
                    {section.title}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </CardContent>
    </Card>
    </Link>
  );
}

type PlanPacing = NonNullable<LearningPlan['pacing']>;

function PacingBanner({
  pacing,
  lang,
  hasDeadline,
}: {
  pacing: PlanPacing;
  lang: Lang;
  hasDeadline: boolean;
}) {
  const t = STR[lang];
  const isHe = lang === 'he';
  // Show the humble, mock-gated, concave readiness (ADR-0010 Stream E) when present;
  // fall back to raw coverage on older payloads.
  const readinessValue = pacing.readiness ?? pacing.goal_readiness ?? 0;
  const readinessPct = Math.round(readinessValue * 100);
  const readinessNote =
    pacing.readiness_message_key === 'day_before'
      ? t.readiness_day_before
      : pacing.readiness_message_key === 'final_phase'
        ? t.readiness_final_phase
        : pacing.exam_ready
          ? t.readiness_exam_ready
          : pacing.readiness != null && pacing.mock_passed === false && (pacing.critical_coverage ?? 0) >= 0.5
            ? t.readiness_needs_mock
            : t.readiness_humble;

  const paceMeta =
    pacing.status === 'ahead'
      ? { label: t.pace_ahead, variant: 'success' as const, bar: 'bg-emerald-500' }
      : pacing.status === 'at_risk'
        ? { label: t.pace_at_risk, variant: 'warning' as const, bar: 'bg-amber-500' }
        : { label: t.pace_on_track, variant: 'secondary' as const, bar: 'bg-primary' };

  return (
    <Card className="glass-surface border-border/60" dir={isHe ? 'rtl' : 'ltr'}>
      <CardContent className="flex flex-wrap items-center justify-between gap-4 py-4">
        <div className="min-w-[180px] flex-1">
          <div className="mb-1 flex items-center justify-between gap-2">
            <span className="text-sm font-medium">{t.readiness_title}</span>
            <span className="text-sm text-muted-foreground">{t.readiness_pct(readinessPct)}</span>
          </div>
          <div className="h-2 rounded-full bg-muted">
            <div
              className={`h-full rounded-full transition-all ${paceMeta.bar}`}
              style={{ width: `${readinessPct}%` }}
              role="progressbar"
              aria-valuenow={readinessPct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={t.readiness_title}
            />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {t.concepts_left(pacing.remaining_scope)}
          </p>
          <p className="mt-1 text-xs text-muted-foreground/80">{readinessNote}</p>
        </div>
        <div className="flex items-center gap-2">
          {hasDeadline ? (
            <Badge variant="outline">{t.weeks_to_goal(pacing.weeks_left)}</Badge>
          ) : null}
          <Badge variant={paceMeta.variant}>{paceMeta.label}</Badge>
        </div>
      </CardContent>
    </Card>
  );
}

function formatShortDate(iso: string, lang: Lang): string {
  try {
    return new Date(iso).toLocaleDateString(lang === 'he' ? 'he-IL' : 'en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

export function LearningPlanDashboard({
  plan,
  finalGoalDate,
  nextTestDate,
}: {
  plan: LearningPlan;
  finalGoalDate?: string | null;
  nextTestDate?: string | null;
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  const week = currentActiveWeek(plan);
  const planEnd = plan.end_date ?? finalGoalDate ?? null;
  const examPrep = examPrepContext(plan, nextTestDate, finalGoalDate);

  return (
    <div className="space-y-8" dir={isHe ? 'rtl' : 'ltr'}>
      <header>
        <h1 className="font-display text-3xl font-bold">{t.title}</h1>
        <p className="mt-2 text-lg font-medium" dir="auto">
          {plan.goal}
        </p>
        {plan.start_date && planEnd ? (
          <p className="mt-1 text-sm text-muted-foreground">
            {t.plan_horizon(
              formatShortDate(plan.start_date, lang),
              formatShortDate(planEnd, lang),
            )}
          </p>
        ) : null}
        {finalGoalDate && !nextTestDate ? (
          <p className="mt-1 text-sm text-muted-foreground">
            {t.target_date(formatShortDate(finalGoalDate, lang))}
          </p>
        ) : null}
        <p className="mt-3 text-xs text-muted-foreground">{t.projected_note}</p>
      </header>

      {plan.pacing ? (
        <PacingBanner
          pacing={plan.pacing}
          lang={lang}
          hasDeadline={Boolean(nextTestDate || finalGoalDate)}
        />
      ) : null}

      {examPrep ? <ExamPrepQuizBanner ctx={examPrep} /> : null}

      {week ? (
        <section className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold">{t.week(week.week_number)}</h2>
              <p className="text-sm text-muted-foreground">
                {t.week_status(week.concepts.length, week.status)}
              </p>
            </div>
            <Button asChild>
              <Link
                href={`/quiz/${week.id}?plan_id=${plan.id}&week_num=${week.week_number}`}
              >
                {t.start_week_quiz}
              </Link>
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {week.concepts.map((concept) => (
              <ConceptCard
                key={concept.concept_id}
                concept={concept}
                lang={lang}
              />
            ))}
          </div>
        </section>
      ) : (
        <p className="text-muted-foreground">{t.no_weeks}</p>
      )}

      {plan.weeks.length > 1 ? (
        <section className="space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground">
            {t.future_weeks}
          </h3>
          <div className="flex flex-wrap gap-2">
            {plan.weeks.map((w) => (
              <Badge
                key={w.id}
                variant={w.status === 'active' ? 'default' : 'outline'}
              >
                {t.week_chip(w.week_number, w.concepts.length)}
              </Badge>
            ))}
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {plan.weeks.map((w) => (
              <Card
                key={w.id}
                className={
                  w.status === 'active' ? 'border-primary/50 bg-primary/5' : 'border-border/60'
                }
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between gap-2">
                    <CardTitle className="text-sm">{t.week(w.week_number)}</CardTitle>
                    <Badge variant={w.status === 'active' ? 'default' : 'outline'}>
                      {lang === 'he' ? statusHe(w.status) : w.status}
                    </Badge>
                  </div>
                  {w.quiz_due_at ? (
                    <p className="text-xs text-muted-foreground">
                      {t.week_until(formatShortDate(w.quiz_due_at, lang))}
                    </p>
                  ) : null}
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {w.concepts.map((c) => (
                      <li key={c.concept_id} dir="auto">
                        {displayName(c, lang)}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
