'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { useI18n } from '@/providers/i18n-provider';

const STR = {
  en: {
    title: 'Building your learning plan',
    sub: 'Creating a 2-week starter plan from your goals…',
    elapsed: (s: number) => `Creating your plan… (${s}s)`,
    error: 'We could not create your plan.',
    retry: 'Try again',
    redirecting: 'Plan ready — opening your dashboard…',
    needsOnboarding: 'Your profile is not complete yet. Returning to the questionnaire…',
    goOnboarding: 'Complete questionnaire →',
  },
  he: {
    title: 'יוצרים את תוכנית הלמידה שלך',
    sub: 'בונים תוכנית ל-2 השבועות הקרובים מהמטרות שמילאת…',
    elapsed: (s: number) => `יוצר את תוכנית הלמידה האישית שלך… (${s} שניות)`,
    error: 'לא הצלחנו ליצור את התוכנית.',
    retry: 'נסה שוב',
    redirecting: 'התוכנית מוכנה — פותחים את לוח הבקרה…',
    needsOnboarding: 'הפרופיל שלך עדיין לא הושלם. חוזרים לשאלון…',
    goOnboarding: 'לחזרה לשאלון →',
  },
} as const;

type PlanExistsCheck = 'yes' | 'no' | 'unknown';

async function checkPlanExists(): Promise<PlanExistsCheck> {
  const res = await fetch('/api/plans/current?exists=1', { cache: 'no-store' });
  if (!res.ok) return 'unknown';
  const data = (await res.json()) as { has_plan?: boolean };
  return data.has_plan ? 'yes' : 'no';
}

type BootstrapResult = { ok: boolean; status?: number; error?: string };

async function bootstrapPlan(replan: boolean): Promise<BootstrapResult> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 25_000);
  try {
    const res = await fetch('/api/plans/bootstrap', {
      method: 'POST',
      signal: controller.signal,
      cache: 'no-store',
    });
    if (res.ok) return { ok: true };
    const text = await res.text();
    let message = text.trim() || `Request failed (${res.status})`;
    try {
      const body = JSON.parse(text) as { error?: string };
      message = body.error ?? message;
    } catch {
      /* plain */
    }
    return { ok: false, status: res.status, error: message };
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      // Server may still have finished — check exists. On a re-plan an existing
      // plan proves nothing (the old plan also "exists"), so skip the shortcut.
      const check = replan ? 'no' : await checkPlanExists();
      if (check === 'yes') return { ok: true };
      if (check === 'unknown') {
        return { ok: false, error: 'Could not verify plan status. Please try again.' };
      }
      return { ok: false, error: 'Plan creation timed out. Please try again.' };
    }
    return {
      ok: false,
      error: err instanceof Error ? err.message : 'Plan creation failed',
    };
  } finally {
    clearTimeout(timeout);
  }
}

export default function PlanSetupPage() {
  const router = useRouter();
  const { locale } = useI18n();
  const lang = locale === 'he' ? 'he' : 'en';
  const t = STR[lang];
  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const [phase, setPhase] = useState<'loading' | 'error' | 'redirecting' | 'needs_onboarding'>(
    'loading',
  );
  const [detail, setDetail] = useState('0');
  const [error, setError] = useState('');
  const started = useRef(false);

  const run = async () => {
    setPhase('loading');
    setError('');
    const t0 = Date.now();
    const tick = window.setInterval(() => {
      setDetail(String(Math.floor((Date.now() - t0) / 1000)));
    }, 1000);

    // ?replan=1 (dashboard "Re-plan" CTA after the plan's end_date passed):
    // the old plan still has status='active', so the exists-check shortcuts
    // would bounce the learner straight back to /app. Force a fresh bootstrap.
    const replan =
      typeof window !== 'undefined' &&
      new URLSearchParams(window.location.search).get('replan') === '1';

    try {
      const initialCheck = replan ? 'no' : await checkPlanExists();
      if (initialCheck === 'unknown') {
        throw new Error(
          lang === 'he'
            ? 'לא הצלחנו לבדוק את סטטוס התוכנית. נסה שוב בעוד רגע.'
            : 'Could not verify plan status. Please try again in a moment.',
        );
      }
      if (initialCheck === 'yes') {
        setPhase('redirecting');
        router.replace('/app');
        return;
      }
      const result = await bootstrapPlan(replan);
      if (!result.ok) {
        // 400 = no profile in DB (onboarding may have aborted before profile commit).
        // Restore draft-based recovery: send learner back to onboarding.
        if (result.status === 400) {
          setPhase('needs_onboarding');
          setTimeout(() => router.replace('/onboarding'), 1500);
          return;
        }
        // One more exists check in case POST timed out after commit
        const retryCheck = replan ? 'no' : await checkPlanExists();
        if (retryCheck === 'yes') {
          setPhase('redirecting');
          router.replace('/app');
          return;
        }
        if (retryCheck === 'unknown') {
          throw new Error(
            lang === 'he'
              ? 'לא הצלחנו לבדוק את סטטוס התוכנית. נסה שוב בעוד רגע.'
              : 'Could not verify plan status. Please try again in a moment.',
          );
        }
        throw new Error(result.error ?? t.error);
      }
      setPhase('redirecting');
      router.replace('/app');
    } catch (err) {
      setPhase('error');
      setError(err instanceof Error ? err.message : t.error);
    } finally {
      window.clearInterval(tick);
    }
  };

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
        {phase === 'needs_onboarding' && (
          <div className="mt-8 space-y-4">
            <p className="text-sm text-muted-foreground">{t.needsOnboarding}</p>
            <button
              type="button"
              onClick={() => router.replace('/onboarding')}
              className="rounded-xl bg-accent-cyan px-6 py-3 text-sm font-semibold text-neutral-950"
            >
              {t.goOnboarding}
            </button>
          </div>
        )}
        {phase === 'error' && (
          <div className="mt-8 space-y-4">
            <p className="text-sm text-destructive" role="alert">
              {error || t.error}
            </p>
            <button
              type="button"
              onClick={() => {
                started.current = false;
                void run().then(() => {
                  started.current = true;
                });
              }}
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
