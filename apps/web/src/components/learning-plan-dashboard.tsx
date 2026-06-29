'use client';

import Link from 'next/link';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Button } from '@asf/ui/button';
import type { LearningPlan, PlanConcept } from '@asf/schemas/learning_path';
import { currentActiveWeek } from '@/lib/learning-path-types';
import { learnConceptHrefFromProfile } from '@/lib/learn-routes';
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
    week_chip: (n: number, c: number) => `שבוע ${n}: ${c} מושגים`,
    no_weeks: 'אין עדיין שבועות בתכנית.',
    progress: 'התקדמות',
    sections_label: 'סעיפים בספר',
    browse_subject: (s: string) => `עיין בתכני ${subjectHe(s)}`,
    not_assessed: 'טרם הוערך',
    mastery_pct: (p: number) => `${p}% שליטה`,
  },
  en: {
    title: 'Your learning plan',
    week: (n: number) => `Week ${n}`,
    week_status: (n: number, status: string) => `${n} concepts · status: ${status}`,
    start_week_quiz: 'Start Week Quiz',
    all_weeks: 'All weeks',
    week_chip: (n: number, c: number) => `Week ${n}: ${c} concepts`,
    no_weeks: 'No weeks in this plan yet.',
    progress: 'Progress',
    sections_label: 'Textbook sections',
    browse_subject: (s: string) => `Browse ${s} content`,
    not_assessed: 'Not assessed',
    mastery_pct: (p: number) => `${p}% mastery`,
  },
} as const;

const SUBJECT_HE: Record<string, string> = {
  math: 'מתמטיקה',
  physics: 'פיזיקה',
  chemistry: 'כימיה',
  biology: 'ביולוגיה',
  cs: 'מדעי המחשב',
  english: 'אנגלית',
};

function subjectHe(s: string): string {
  return SUBJECT_HE[s.toLowerCase()] ?? s;
}

const STATUS_HE: Record<string, string> = {
  active: 'פעיל',
  upcoming: 'עתידי',
  completed: 'הושלם',
  skipped: 'דולג',
};

function statusHe(status: string): string {
  return STATUS_HE[status.toLowerCase()] ?? status;
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
  if (lang === 'he' && concept.name_he && concept.name_he.trim().length > 0) {
    return concept.name_he;
  }
  return concept.name;
}

function ConceptCard({ concept, lang }: { concept: PlanConcept; lang: Lang }) {
  const t = STR[lang];
  const isHe = lang === 'he';
  const mastery = concept.mastery ?? 0;
  const progressPct = Math.round(mastery * 100);
  const name = displayName(concept, lang);
  const lessonHref = learnConceptHrefFromProfile(concept.concept_id, concept.subject);

  return (
    <Link href={lessonHref} className="block transition-opacity hover:opacity-90">
    <Card className="glass-surface border-border/60" dir={isHe ? 'rtl' : 'ltr'}>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <CardTitle className="text-base" dir="auto">
            {name}
          </CardTitle>
          <Badge variant={masteryBadgeVariant(concept.mastery)}>
            {masteryLabel(concept.mastery, lang)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
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

        {concept.suggested_sections.length > 0 ? (
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

export function LearningPlanDashboard({ plan }: { plan: LearningPlan }) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  const week = currentActiveWeek(plan);

  return (
    <div className="space-y-8" dir={isHe ? 'rtl' : 'ltr'}>
      <header>
        <h1 className="font-display text-3xl font-bold">{t.title}</h1>
        {/* `goal` is free-text the learner wrote during onboarding; let the
            browser pick direction per their actual string. */}
        <p className="mt-2 text-muted-foreground" dir="auto">
          {plan.goal}
        </p>
      </header>

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
        <section>
          <h3 className="mb-3 text-sm font-medium text-muted-foreground">
            {t.all_weeks}
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
        </section>
      ) : null}
    </div>
  );
}
