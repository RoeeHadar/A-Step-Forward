/**
 * /app/practice/history — review past practice sessions.
 */
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { listPracticeSessionsForLearner } from '@/lib/practice-session';
import { practiceTopicLabels } from '@/lib/practice-topics';
import { cookies } from 'next/headers';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';

export const dynamic = 'force-dynamic';

export default async function PracticeHistoryPage() {
  const ctx = await getAuthContext();
  if (!ctx) redirect('/sign-in');
  const cookieStore = await cookies();
  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);
  const he = locale === 'he';

  const rows = await listPracticeSessionsForLearner(ctx.userId, 40);

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-8">
      <header className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {he ? 'זירת תרגול' : 'Practice arena'}
        </p>
        <h1 className="font-display text-2xl font-semibold">
          {he ? 'היסטוריית תרגולים' : 'Practice history'}
        </h1>
        <Link href="/app/practice" className="text-sm text-primary underline-offset-2 hover:underline">
          {he ? 'חזרה לתרגול' : 'Back to practice'}
        </Link>
      </header>

      {!rows.length ? (
        <p className="text-sm text-muted-foreground">
          {he ? 'עדיין אין סשנים.' : 'No sessions yet.'}
        </p>
      ) : (
        <ul className="space-y-3">
          {rows.map((r) => {
            const labels = practiceTopicLabels(r.topic_ids, he ? 'he' : 'en');
            return (
              <li
                key={r.id}
                className="rounded-xl border border-border/60 bg-surface-1/40 px-4 py-3 text-sm"
              >
                <Link
                  href={`/app/practice/history/${r.id}`}
                  className="font-medium text-foreground underline-offset-2 hover:underline"
                >
                  {r.created_at
                    ? new Date(r.created_at).toLocaleString(he ? 'he-IL' : 'en-GB')
                    : r.id.slice(0, 8)}
                </Link>
                <p className="mt-1 text-muted-foreground">
                  {r.status} · {r.correct_count}/{r.attempted}
                  {labels.length ? ` · ${labels.join(', ')}` : ''}
                </p>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
