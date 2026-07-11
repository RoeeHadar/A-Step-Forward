'use client';

import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { useLanguagePreference } from '@/hooks/use-language-preference';

/**
 * Empty state shown on /dashboard when the learner has no learning plan yet.
 */
const STR = {
  he: {
    title: 'אין עדיין תכנית לימוד',
    blurb: 'השלם/י את שאלון ההיכרות או צור/י תוכנית מהמטרות שכבר מילאת.',
    ctaOnboarding: 'השלם/י שאלון',
    ctaPlan: 'צור/י תוכנית עכשיו',
    back: 'חזרה לאפליקציה',
  },
  en: {
    title: 'No learning plan yet',
    blurb: 'Finish the onboarding questionnaire or generate a plan from the goals you already shared.',
    ctaOnboarding: 'Complete onboarding',
    ctaPlan: 'Create my plan',
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
          <Link href="/onboarding">{t.ctaOnboarding}</Link>
        </Button>
        <Button variant="secondary" asChild>
          <Link href="/plan-setup">{t.ctaPlan}</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/app">{t.back}</Link>
        </Button>
      </div>
    </div>
  );
}
