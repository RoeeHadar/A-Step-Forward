'use client';

import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { useLanguagePreference } from '@/hooks/use-language-preference';

/**
 * Bilingual fallback shown on /quiz/[week_id] when we can't fetch the
 * questions for the requested week. Mirrors the look of the no-plan
 * empty state on /dashboard.
 */
const STR = {
  he: {
    title: 'המבחן לא זמין',
    blurb: 'לא הצלחנו לטעון את המבחן. נסה שוב מהלוח.',
    cta: 'חזרה ללוח',
  },
  en: {
    title: 'Quiz unavailable',
    blurb: 'Unable to load the quiz. Please try again from your dashboard.',
    cta: 'Back to dashboard',
  },
} as const;

export function QuizUnavailable() {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  return (
    <div
      className="glass-surface rounded-2xl p-8 text-center"
      dir={isHe ? 'rtl' : 'ltr'}
    >
      <h1 className="font-display text-2xl font-bold">{t.title}</h1>
      <p className="mt-2 text-muted-foreground">{t.blurb}</p>
      <div className="mt-6 flex justify-center">
        <Button asChild>
          <Link href="/dashboard">{t.cta}</Link>
        </Button>
      </div>
    </div>
  );
}
