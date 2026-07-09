'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { CheckCircle2, X } from 'lucide-react';
import { Card, CardContent } from '@asf/ui/card';
import { Button } from '@asf/ui/button';
import { resolveConceptTitles } from '@/lib/concept-display-names';
import type { PlanChangeHistoryEntry } from '@/lib/neon-db';
import { useLanguagePreference, type Lang } from '@/hooks/use-language-preference';

function dismissedPlanChangeStorageKey(learnerId: string): string {
  return `asf-plan-change-dismissed-${learnerId}`;
}

const STR = {
  he: {
    title: 'המטרה והתוכנית עודכנו',
    reason: (r: string) => `סיבה: ${r}`,
    goal: (g: string) => `מטרה: ${g}`,
    weekPreview: 'תצוגה מקדימה:',
    weekLine: (n: number, names: string) => `שבוע ${n}: ${names}`,
    viewPlan: 'צפה בכל השבועות',
    futureNote:
      'שבועות עתידיים עשויים להשתנות בהתאם להתקדמות שלך במבחנים ובתרגילים.',
    close: 'סגור הודעה',
  },
  en: {
    title: 'Your goal and plan were updated',
    reason: (r: string) => `Reason: ${r}`,
    goal: (g: string) => `Goal: ${g}`,
    weekPreview: 'Preview:',
    weekLine: (n: number, names: string) => `Week ${n}: ${names}`,
    viewPlan: 'View full plan',
    futureNote: 'Future weeks may shift based on your quiz and practice performance.',
    close: 'Dismiss plan update notice',
  },
} as const;

function conceptNames(ids: string[], lang: Lang): string {
  return ids
    .map((id) => {
      const t = resolveConceptTitles(id);
      return lang === 'he' ? t.title_he ?? t.title_en : t.title_en;
    })
    .join(', ');
}

export function PlanChangeBanner({
  change,
  learnerId,
}: {
  change: PlanChangeHistoryEntry;
  learnerId: string;
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  const [visible, setVisible] = useState(false);
  const changedAt = new Date(change.at);
  const isRecent =
    Number.isFinite(changedAt.getTime()) &&
    Date.now() - changedAt.getTime() < 7 * 24 * 60 * 60 * 1000;

  useEffect(() => {
    if (!isRecent) {
      setVisible(false);
      return;
    }
    const dismissedId = localStorage.getItem(dismissedPlanChangeStorageKey(learnerId));
    setVisible(dismissedId !== change.id);
  }, [change.id, isRecent, learnerId]);

  function dismiss() {
    localStorage.setItem(dismissedPlanChangeStorageKey(learnerId), change.id);
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <Card
      className="relative mb-6 border-emerald-500/40 bg-emerald-500/5"
      dir={isHe ? 'rtl' : 'ltr'}
      role="status"
    >
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute end-2 top-2 h-8 w-8 text-muted-foreground hover:text-foreground"
        onClick={dismiss}
        aria-label={t.close}
      >
        <X className="h-4 w-4" aria-hidden />
      </Button>
      <CardContent className="flex flex-col gap-3 p-4 pe-12 sm:flex-row sm:items-start sm:justify-between sm:pe-4">
        <div className="flex gap-3">
          <CheckCircle2
            className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600"
            aria-hidden
          />
          <div className="space-y-2">
            <p className="font-semibold text-emerald-800 dark:text-emerald-300">
              {t.title}
            </p>
            {change.goal ? (
              <p className="text-sm font-medium" dir="auto">
                {t.goal(change.goal)}
              </p>
            ) : null}
            {change.reason ? (
              <p className="text-sm text-muted-foreground">{t.reason(change.reason)}</p>
            ) : null}
            {change.week_preview?.length ? (
              <div className="text-sm">
                <p className="font-medium text-muted-foreground">{t.weekPreview}</p>
                <ul className="mt-1 space-y-0.5">
                  {change.week_preview.map((w) => (
                    <li key={w.week} dir="auto">
                      {t.weekLine(w.week, conceptNames(w.conceptIds, lang))}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
            <p className="text-xs text-muted-foreground">{t.futureNote}</p>
          </div>
        </div>
        <Link
          href="/app/plan"
          className="shrink-0 text-sm font-medium text-primary hover:underline"
        >
          {t.viewPlan}
        </Link>
      </CardContent>
    </Card>
  );
}
