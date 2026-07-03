'use client';

import Link from 'next/link';
import { ClipboardCheck } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useLanguagePreference } from '@/hooks/use-language-preference';

const STR = {
  he: {
    title: (n: number) =>
      n <= 7 ? 'שבוע ההכנה למבחן — זמן למבחן תרגול!' : 'המבחן מתקרב — מומלץ מבחן תרגול',
    body: (n: number) =>
      n <= 7
        ? `נשארו ${n} ימים ליעד. עברו על מבחן שבועי (או כמה מבחנים קצרים) כדי לזהות פערים לפני המבחן.`
        : `נשארו ${n} ימים ליעד. מומלץ להתחיל מבחני תרגול על הנושאים בתוכנית השבועית.`,
    weekQuiz: 'מבחן שבועי',
    customQuiz: 'מבחן מותאם',
  },
  en: {
    title: (n: number) =>
      n <= 7 ? 'Exam prep week — time for practice quizzes!' : 'Your goal is near — take a practice quiz',
    body: (n: number) =>
      n <= 7
        ? `${n} days until your target. Take the week quiz (or a few short quizzes) to find gaps before the exam.`
        : `${n} days until your target. Start practice quizzes on this week's plan topics.`,
    weekQuiz: 'Week quiz',
    customQuiz: 'Custom quiz',
  },
} as const;

export function ExamPrepQuizBanner({
  ctx,
}: {
  ctx: {
    daysLeft: number;
    weekId?: string;
    weekNumber?: number;
    planId?: string;
  };
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';

  const weekQuizHref =
    ctx.weekId && ctx.planId && ctx.weekNumber != null
      ? `/quiz/${ctx.weekId}?plan_id=${ctx.planId}&week_num=${ctx.weekNumber}`
      : '/app/quiz';

  return (
    <div
      className="rounded-2xl border border-amber-500/40 bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent p-5 shadow-sm"
      dir={isHe ? 'rtl' : 'ltr'}
      role="status"
    >
      <div className="flex flex-wrap items-start gap-4">
        <span
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 text-amber-700 dark:text-amber-300"
          aria-hidden
        >
          <ClipboardCheck className="h-6 w-6" />
        </span>
        <div className="min-w-0 flex-1 space-y-2">
          <h2 className="font-display text-lg font-semibold text-foreground">
            {t.title(ctx.daysLeft)}
          </h2>
          <p className="text-sm text-muted-foreground">{t.body(ctx.daysLeft)}</p>
          <div className="flex flex-wrap gap-2 pt-1">
            <Button asChild size="sm">
              <Link href={weekQuizHref}>{t.weekQuiz}</Link>
            </Button>
            <Button asChild size="sm" variant="outline">
              <Link href="/app/quiz">{t.customQuiz}</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
