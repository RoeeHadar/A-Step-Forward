'use client';

import { useState, useTransition } from 'react';
import Link from 'next/link';
import { Sparkles, Target } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';
import type { GoalCompletionStatus } from '@/lib/neon-db';

const STR = {
  he: {
    minorTitle: 'סיימת את יעד השבוע! 🎉',
    minorBody:
      'כל המושגים בשבוע הפעיל שלך בשליטה. הגדר יעד חדש כדי שנעדכן את תכנית הלימוד שלך.',
    majorTitle: 'השלמת את יעד הלימוד הגדול! 🏆',
    majorBody:
      'עברת על כל המושגים בתכנית הנוכחית. הגיע הזמן ליעד חדש — בגרות, מבחן, או נושא שתרצה לחזק.',
    setGoal: 'הגדר יעד חדש',
    regenerate: 'עדכן תכנית',
    dismiss: 'אחר כך',
    regenerating: 'מעדכן…',
  },
  en: {
    minorTitle: 'Weekly goal complete! 🎉',
    minorBody:
      'You mastered every concept in your active week. Set a new focus so we can refresh your learning plan.',
    majorTitle: 'Major goal complete! 🏆',
    majorBody:
      'You finished every concept in your current plan. Time for a new goal — exam prep, Bagrut, or a topic to strengthen.',
    setGoal: 'Set a new goal',
    regenerate: 'Refresh plan',
    dismiss: 'Later',
    regenerating: 'Updating…',
  },
} as const;

export function GoalCompletionBanner({ status }: { status: GoalCompletionStatus }) {
  const { locale } = useI18n();
  const t = STR[locale];
  const isHe = locale === 'he';
  const [dismissed, setDismissed] = useState(false);
  const [pending, startTransition] = useTransition();
  const [regenerated, setRegenerated] = useState(false);

  if (dismissed || regenerated) return null;
  if (!status.minorComplete && !status.majorComplete) return null;

  const isMajor = status.majorComplete;
  const title = isMajor ? t.majorTitle : t.minorTitle;
  const body = isMajor ? t.majorBody : t.minorBody;

  const regeneratePlan = () => {
    startTransition(async () => {
      try {
        await fetch('/api/plans/generate', { method: 'POST' });
        setRegenerated(true);
      } catch {
        // Keep banner visible so the learner can retry or set a goal manually.
      }
    });
  };

  return (
    <div
      className="iridescent-border mb-6 flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
      dir={isHe ? 'rtl' : 'ltr'}
      role="status"
    >
      <div className="flex min-w-0 gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent-magenta text-primary-foreground">
          {isMajor ? (
            <Target className="h-5 w-5" aria-hidden />
          ) : (
            <Sparkles className="h-5 w-5" aria-hidden />
          )}
        </div>
        <div>
          <p className="font-display text-lg font-bold">{title}</p>
          <p className="mt-1 text-sm text-muted-foreground">{body}</p>
          {status.planGoal ? (
            <p className="mt-1 text-xs text-muted-foreground" dir="auto">
              {status.planGoal}
            </p>
          ) : null}
        </div>
      </div>
      <div className="flex shrink-0 flex-wrap gap-2">
        <Button variant="outline" size="sm" onClick={() => setDismissed(true)}>
          {t.dismiss}
        </Button>
        <Button variant="secondary" size="sm" onClick={regeneratePlan} disabled={pending}>
          {pending ? t.regenerating : t.regenerate}
        </Button>
        <Button asChild size="sm">
          <Link href="/onboarding">{t.setGoal}</Link>
        </Button>
      </div>
    </div>
  );
}
