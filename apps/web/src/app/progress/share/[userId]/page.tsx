import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { getPublicShareStats } from '@/lib/neon-db';
import { getServerLocale } from '@/i18n/locale-server';

export const dynamic = 'force-dynamic';

function formatDate(iso: string | null, locale: 'he' | 'en'): string {
  if (!iso) return locale === 'he' ? '—' : '—';
  try {
    return new Date(iso).toLocaleDateString(locale === 'he' ? 'he-IL' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso.slice(0, 10);
  }
}

function subjectLabel(subject: string | null, isHe: boolean): string {
  if (!subject) return isHe ? 'מתמטיקה' : 'Math';
  if (subject === 'hs_physics') return isHe ? 'פיזיקה' : 'Physics';
  const m = subject.match(/math_(\d)/);
  if (m) return isHe ? `מתמטיקה ${m[1]} יח'` : `Math (${m[1]}pt)`;
  return isHe ? 'מתמטיקה' : 'Math';
}

export default async function PublicProgressSharePage({
  params,
}: {
  params: Promise<{ userId: string }>;
}) {
  const { userId } = await params;
  const locale = await getServerLocale();
  const isHe = locale === 'he';
  const stats = await getPublicShareStats(userId);

  if (!stats) notFound();

  const masteryPct = Math.round(stats.mastery_avg * 100);
  const studyingDays = stats.streak_days > 0 ? stats.streak_days : stats.lessons_completed_count > 0 ? 1 : 0;

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main
        className="mx-auto w-full max-w-lg flex-1 px-4 py-12"
        dir={isHe ? 'rtl' : 'ltr'}
      >
        <h1 className="font-display text-3xl font-bold">
          {isHe ? 'דו״ח התקדמות' : 'Progress Report'}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {isHe
            ? 'סיכום למידה — ללא פרטים אישיים'
            : 'Learning summary — no personal details'}
        </p>

        <div className="card-punch mt-8 space-y-4 rounded-2xl p-6">
          <p className="text-base leading-relaxed text-foreground">
            {isHe ? (
              <>
                לומד/ת כבר <strong>{studyingDays}</strong> ימים · השלים/ה{' '}
                <strong>{stats.lessons_completed_count}</strong> שיעורים · שליטה:{' '}
                <strong>{masteryPct}%</strong> · פעילות אחרונה:{' '}
                <strong>{formatDate(stats.last_active_date, locale)}</strong>
              </>
            ) : (
              <>
                Studying for <strong>{studyingDays}</strong> days · Completed{' '}
                <strong>{stats.lessons_completed_count}</strong> lessons · Mastery:{' '}
                <strong>{masteryPct}%</strong> · Last active:{' '}
                <strong>{formatDate(stats.last_active_date, locale)}</strong>
              </>
            )}
          </p>

          {stats.estimated_grade != null ? (
            <div className="border-t border-border pt-3">
              <p className="text-sm font-semibold text-foreground">
                {isHe ? 'ציון משוער לבגרות' : 'Estimated Bagrut grade'}
                {stats.subject ? ` (${subjectLabel(stats.subject, isHe)})` : ''}
              </p>
              <p className="mt-1 text-2xl font-bold text-primary">
                ~{stats.estimated_grade}
              </p>
            </div>
          ) : null}

          {stats.week_activity.length === 7 ? (
            <div className="border-t border-border pt-3">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                {isHe ? 'פעילות שבועית' : 'Week activity'}
              </p>
              <div className="flex gap-1.5">
                {stats.week_activity.map((active, i) => (
                  <div
                    key={i}
                    className={`h-6 w-6 rounded-sm ${active ? 'bg-primary' : 'bg-muted'}`}
                    title={active ? (isHe ? 'פעיל' : 'Active') : (isHe ? 'לא פעיל' : 'Inactive')}
                  />
                ))}
              </div>
            </div>
          ) : null}
        </div>

        <div className="mt-8 text-center">
          <Link
            href="/onboarding"
            className="inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-5 py-2.5 text-sm font-semibold text-primary-foreground"
          >
            {isHe ? 'התחילו את מסע הלמידה שלכם' : 'Start your own learning journey'}
          </Link>
        </div>
      </main>
    </div>
  );
}
