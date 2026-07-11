'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { useI18n } from '@/providers/i18n-provider';
import { generatePlanWithRetry } from '@/lib/diagnostic-plan-client';

const STR = {
  en: {
    title: 'Building your learning plan',
    sub: 'We are creating a weekly plan from your goals. This usually takes a few seconds.',
    elapsed: (s: number) => `Creating your plan… (${s}s)`,
    error: 'We could not create your plan.',
    retry: 'Try again',
    redirecting: 'Plan ready — opening your dashboard…',
  },
  he: {
    title: 'יוצרים את תוכנית הלמידה שלך',
    sub: 'אנחנו בונים תוכנית שבועית מהמטרות שמילאת. זה לוקח בדרך כלל כמה שניות.',
    elapsed: (s: number) => `יוצר את תוכנית הלמידה האישית שלך… (${s} שניות)`,
    error: 'לא הצלחנו ליצור את התוכנית.',
    retry: 'נסה שוב',
    redirecting: 'התוכנית מוכנה — פותחים את לוח הבקרה…',
  },
} as const;

export default function PlanSetupPage() {
  const router = useRouter();
  const { locale } = useI18n();
  const lang = locale === 'he' ? 'he' : 'en';
  const t = STR[lang];
  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const [phase, setPhase] = useState<'loading' | 'error' | 'redirecting'>('loading');
  const [detail, setDetail] = useState('0');
  const [error, setError] = useState('');
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    void (async () => {
      setPhase('loading');
      setError('');
      try {
        await generatePlanWithRetry({
          onPhase: (p, d) => {
            if (p === 'redirecting') setPhase('redirecting');
            if (p === 'generating_plan' && d) setDetail(d);
          },
        });
        router.replace('/app');
      } catch (err) {
        setPhase('error');
        setError(err instanceof Error ? err.message : t.error);
      }
    })();
  }, [router, t.error]);

  const retry = () => {
    started.current = false;
    setPhase('loading');
    setError('');
    void (async () => {
      started.current = true;
      try {
        await generatePlanWithRetry({
          onPhase: (p, d) => {
            if (p === 'redirecting') setPhase('redirecting');
            if (p === 'generating_plan' && d) setDetail(d);
          },
        });
        router.replace('/app');
      } catch (err) {
        setPhase('error');
        setError(err instanceof Error ? err.message : t.error);
      }
    })();
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader />
      <main className="mx-auto max-w-lg px-4 py-16 text-center" dir={dir}>
        <h1 className="text-2xl font-bold">{t.title}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{t.sub}</p>
        {phase === 'loading' && (
          <p className="mt-8 text-base text-accent-cyan">{t.elapsed(Number(detail) || 0)}</p>
        )}
        {phase === 'redirecting' && (
          <p className="mt-8 text-base text-accent-cyan">{t.redirecting}</p>
        )}
        {phase === 'error' && (
          <div className="mt-8 space-y-4">
            <p className="text-sm text-destructive" role="alert">
              {error || t.error}
            </p>
            <button
              type="button"
              onClick={retry}
              className="rounded-xl bg-accent-cyan px-6 py-3 text-sm font-semibold text-neutral-950"
            >
              {t.retry}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
