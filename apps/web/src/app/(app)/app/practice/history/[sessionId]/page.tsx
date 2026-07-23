/**
 * /app/practice/history/[sessionId] — one session review for the learner.
 */
import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { getPracticeSessionForLearner } from '@/lib/practice-session';
import { practiceTopicLabels } from '@/lib/practice-topics';
import { cookies } from 'next/headers';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';
import { MarkdownMath } from '@/components/markdown-math';

export const dynamic = 'force-dynamic';

export default async function PracticeSessionReviewPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const ctx = await getAuthContext();
  if (!ctx) redirect('/sign-in');
  const { sessionId } = await params;
  const row = await getPracticeSessionForLearner(ctx.userId, sessionId);
  if (!row) notFound();

  const cookieStore = await cookies();
  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);
  const he = locale === 'he';
  const labels = practiceTopicLabels(row.topic_ids, he ? 'he' : 'en');
  const summary = row.summary;

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-8">
      <header className="space-y-2">
        <Link
          href="/app/practice/history"
          className="text-sm text-primary underline-offset-2 hover:underline"
        >
          {he ? '← היסטוריה' : '← History'}
        </Link>
        <h1 className="font-display text-2xl font-semibold">
          {he ? 'סיכום סשן' : 'Session review'}
        </h1>
        <p className="text-sm text-muted-foreground">
          {row.correct_count}/{row.attempted}
          {labels.length ? ` · ${labels.join(', ')}` : ''}
          {summary?.avg_process_score != null
            ? ` · ${(summary.avg_process_score * 100).toFixed(0)}%`
            : ''}
        </p>
      </header>

      <ul className="space-y-4">
        {(summary?.attempts ?? row.attempt_log).map((a, i) => (
          <li
            key={`${a.item_id}-${i}`}
            className="rounded-xl border border-border/60 bg-surface-1/40 p-4 text-sm"
          >
            <p className="mb-2 text-xs text-muted-foreground">
              {a.kind} · {a.difficulty} · {a.correct ? (he ? 'הצלחה' : 'ok') : he ? 'לא' : 'miss'}
              {a.process_score != null ? ` · ${(a.process_score * 100).toFixed(0)}%` : ''}
            </p>
            <div className="prose prose-sm dark:prose-invert max-w-none" dir={he ? 'rtl' : 'ltr'}>
              <MarkdownMath>{he ? a.stem_he : a.stem_en}</MarkdownMath>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
