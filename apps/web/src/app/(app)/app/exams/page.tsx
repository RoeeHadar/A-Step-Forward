'use client';

import Link from 'next/link';
import { ClipboardList } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { EXAM_FORMAT_DISCLAIMER } from '@/lib/exam-disclaimer';

const STR = {
  he: {
    title: 'תרגולי בחינה',
    mcqTitle: 'תרגול עם שאלות אמריקאיות',
    mcqDesc: 'מבחן מוגבל בזמן עם שאלות אמריקאיות ותשובות קצרות — לחיזוק ידע, לא לדמיין בגרות.',
    start: 'התחל תרגול',
  },
  en: {
    title: 'Practice Tests',
    mcqTitle: 'MCQ Practice Set',
    mcqDesc: 'Timed practice with multiple-choice and short-answer questions — builds knowledge, not a Bagrut replica.',
    start: 'Start practice',
  },
} as const;

export default function ExamsPage() {
  const [locale] = useLanguagePreference('he');
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];
  const disclaimer = EXAM_FORMAT_DISCLAIMER[isHe ? 'he' : 'en'];

  return (
    <div className="mx-auto max-w-2xl px-4 py-8" dir={isHe ? 'rtl' : 'ltr'}>
      <h1 className="font-display text-3xl font-bold">{t.title}</h1>

      <p className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm leading-relaxed text-foreground">
        {disclaimer}
      </p>

      <div className="card-punch mt-8 flex items-start gap-4 rounded-2xl p-5">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-accent-amber to-accent-magenta text-primary-foreground">
          <ClipboardList className="h-6 w-6" aria-hidden />
        </span>
        <div className="min-w-0 flex-1">
          <h2 className="font-display text-lg font-semibold">{t.mcqTitle}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{t.mcqDesc}</p>
          <Button asChild className="mt-4">
            <Link href="/app/quiz/mock-exam">{t.start}</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
