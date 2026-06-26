'use client';

import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { useLanguagePreference } from '@/hooks/use-language-preference';

/**
 * Empty state shown on /dashboard when the learner has no learning plan yet.
 * Pulled out of the server page so we can use the language-preference hook
 * for full bilingual rendering (HE default, RTL when HE).
 */
const STR = {
  he: {
    title: 'אין עדיין תכנית לימוד',
    blurb: 'השלם את שאלון האבחון כדי לקבל תכנית שבועית מותאמת אישית.',
    cta: 'התחל אבחון',
    back: 'חזרה לאפליקציה',
  },
  en: {
    title: 'No learning plan yet',
    blurb:
      'Complete the diagnostic assessment to generate your personalized weekly plan.',
    cta: 'Start diagnostic',
    back: 'Back to app',
  },
} as const;

export function NoPlanEmptyState() {
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
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Button asChild>
          <Link href="/diagnostic">{t.cta}</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/app">{t.back}</Link>
        </Button>
      </div>
    </div>
  );
}
